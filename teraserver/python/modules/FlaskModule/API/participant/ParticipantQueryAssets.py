from flask import session, request
from flask_restx import Resource, inputs
from modules.LoginModule.LoginModule import participant_multi_auth
from modules.Globals import db_man
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraAsset import TeraAsset

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('asset_uuid', type=str, help='Asset UUID to query', default=None)
get_parser.add_argument('id_asset', type=int, help='Asset ID to query', default=None)
get_parser.add_argument('with_urls', type=inputs.boolean, help='Also include assets infos and download-upload url')


class ParticipantQueryAssets(Resource):

    def __init__(self, _api, flaskModule = None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @participant_multi_auth.login_required(role='full')
    @api.expect(get_parser)
    @api.doc(description='Get participant assets based on the ID or, if no parameters, get all assets',
             responses={200: 'Success',
                        403: 'Participant doesn\'t have access to the specified asset'})
    def get(self):

        participant = TeraParticipant.get_participant_by_uuid(session['_user_id'])
        args = get_parser.parse_args()

        participant_access = db_man.participantAccess(participant)
        assets = participant_access.get_accessible_assets(id_asset=args['id_asset'], uuid_asset=args['asset_uuid'])

        # Create response
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']
        access_token = None
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']
        services_infos = []
        if args['with_urls']:
            services_infos = {service.service_uuid: service.service_clientendpoint
                              for service in participant_access.get_accessible_services()}

            # Access token
            from opentera.redis.RedisVars import RedisVars
            token_key = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
            access_token = TeraAsset.get_access_token(asset_uuids=[asset.asset_uuid for asset in assets],
                                                      token_key=token_key, requester_uuid=participant.participant_uuid,
                                                      expiration=1800)

        assets_json = []
        for asset in assets:
            asset_json = asset.to_json()

            if args['with_urls']:
                # We have previously verified that the service is available to the user
                if asset.asset_service_uuid in services_infos:
                    asset_json['asset_infos_url'] = 'https://' + servername + ':' + str(port) \
                                                    + services_infos[asset.asset_service_uuid] \
                                                    + '/api/assets/infos?asset_uuid=' + asset.asset_uuid
                    asset_json['asset_url'] = 'https://' + servername + ':' + str(port) \
                                              + services_infos[asset.asset_service_uuid] \
                                              + '/api/assets?asset_uuid=' + asset.asset_uuid

                    if not assets_json:
                        # Append access token to first item only
                        asset_json['access_token'] = access_token

                else:
                    # Service not found or unavaiable for current user
                    asset_json['asset_infos_url'] = None
                    asset_json['asset_url'] = None

            assets_json.append(asset_json)

        return assets_json

