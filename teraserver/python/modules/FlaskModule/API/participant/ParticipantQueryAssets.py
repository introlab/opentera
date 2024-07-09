from flask import session, request
from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import participant_multi_auth, current_participant
from modules.DatabaseModule.DBManager import DBManager
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraAsset import TeraAsset

from opentera.redis.RedisVars import RedisVars

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('asset_uuid', type=str, help='Asset UUID to query', default=None)
get_parser.add_argument('id_asset', type=int, help='Asset ID to query', default=None)
get_parser.add_argument('id_session', type=int, help='Session ID to query assets for', default=None)
get_parser.add_argument('with_urls', type=inputs.boolean, help='Also include assets infos and download-upload url')
get_parser.add_argument('with_only_token', type=inputs.boolean, help='Only includes the access token. '
                                                                     'Will ignore with_urls if specified.')


class ParticipantQueryAssets(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get participant assets based on the ID or, if no parameters, get all assets',
             responses={200: 'Success',
                        403: 'Participant doesn\'t have access to the specified asset'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @participant_multi_auth.login_required(role='limited')
    def get(self):
        args = get_parser.parse_args()
        participant_access = DBManager.participantAccess(current_participant)

        if not current_participant.fullAccess:
            # Not full access = can only query by id_asset or id_session
            if not args['id_session'] and not args['id_asset'] and not args['asset_uuid']:
                return gettext('Forbidden'), 403

        if args['id_session']:
            if args['id_session'] not in participant_access.get_accessible_sessions_ids():
                return gettext('No access to session'), 403

        assets = participant_access.get_accessible_assets(id_asset=args['id_asset'], uuid_asset=args['asset_uuid'],
                                                          session_id=args['id_session'])

        # Create response
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']
        access_token = None
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']
        services_infos = []
        if (args['with_urls'] or args['with_only_token']) and assets and current_participant.fullAccess:
            services_infos = {service.service_uuid: service.service_clientendpoint
                              for service in participant_access.get_accessible_services()}

        assets_json = []
        for asset in assets:
            if args['with_only_token'] and current_participant.fullAccess:
                asset_json = {'asset_uuid': asset.asset_uuid}
            else:
                asset_json = asset.to_json()

            # Access token
            if (args['with_urls'] or args['with_only_token']) and current_participant.fullAccess:
                # Access token
                token_key = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
                access_token = TeraAsset.get_access_token(asset_uuids=asset.asset_uuid,
                                                          token_key=token_key,
                                                          requester_uuid=current_participant.participant_uuid,
                                                          expiration=1800)
                asset_json['access_token'] = access_token
            if args['with_urls'] and current_participant.fullAccess:
                # We have previously verified that the service is available to the user
                if asset.asset_service_uuid in services_infos:
                    asset_json['asset_infos_url'] = 'https://' + servername + ':' + str(port) \
                                                    + services_infos[asset.asset_service_uuid] \
                                                    + '/api/assets/infos'  # ?asset_uuid=' + asset.asset_uuid
                    asset_json['asset_url'] = 'https://' + servername + ':' + str(port) \
                                              + services_infos[asset.asset_service_uuid] \
                                              + '/api/assets'  # ?asset_uuid=' + asset.asset_uuid

                else:
                    # Service not found or unavaiable for current user
                    asset_json['asset_infos_url'] = None
                    asset_json['asset_url'] = None

            assets_json.append(asset_json)

        return assets_json

