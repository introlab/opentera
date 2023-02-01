from flask import session, request
from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraService import TeraService

from modules.DatabaseModule.DBManager import DBManager
from opentera.redis.RedisVars import RedisVars

# Parser definition(s)
# GET
get_parser = api.parser()
get_parser.add_argument('id_asset', type=int, help='Specific ID of asset to query information.')
get_parser.add_argument('asset_uuid', type=str, help='Specific UUID of asset to query information.')
get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all assets')
get_parser.add_argument('id_session', type=int, help='ID of session from which to request all assets')
get_parser.add_argument('id_participant', type=int, help='ID of participant from which to request all assets')
get_parser.add_argument('id_user', type=int, help='ID of the user from which to request all assets.')
get_parser.add_argument('service_uuid', type=str, help='Query all assets associated with that service uuid')
get_parser.add_argument('id_creator_service', type=int, help='ID of the service from which to request all created '
                                                             'assets.')
get_parser.add_argument('id_creator_user', type=int, help='ID of the user from which to request all created assets.')
get_parser.add_argument('id_creator_participant', type=int, help='ID of the participant from which to request all '
                                                                 'created assets.')
get_parser.add_argument('id_creator_device', type=int, help='ID of the device from which to request all created '
                                                            'assets.')

get_parser.add_argument('with_urls', type=inputs.boolean, help='Also include assets infos and download-upload url')
get_parser.add_argument('with_only_token', type=inputs.boolean, help='Only includes the access token. '
                                                                     'Will ignore with_urls if specified.')
get_parser.add_argument('full', type=inputs.boolean, help='Also include names of sessions, users, services, ... in the '
                                                          'reply')
get_parser.add_argument('token', type=str, help='Secret Token')


class UserQueryAssets(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get asset information. Only one of the ID parameter is supported at once',
             responses={200: 'Success - returns list of assets',
                        400: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        user_access = DBManager.userAccess(current_user)

        args = get_parser.parse_args()

        # At least one argument required
        if not any(args.values()):
            return gettext('No arguments specified'), 400
        elif args['id_device']:
            if args['id_device'] not in user_access.get_accessible_devices_ids():
                return gettext('Device access denied'), 403
            assets = TeraAsset.get_assets_for_device(device_id=args['id_device'])
        elif args['id_session']:
            if not user_access.query_session(session_id=args['id_session']):
                return gettext('Session access denied'), 403
            assets = TeraAsset.get_assets_for_session(session_id=args['id_session'])
        elif args['id_participant']:
            if args['id_participant'] not in user_access.get_accessible_participants_ids():
                return gettext('Participant access denied'), 403
            assets = TeraAsset.get_assets_for_participant(part_id=args['id_participant'])
        elif args['id_user']:
            if args['id_user'] not in user_access.get_accessible_users_ids():
                return gettext("User access denied"), 403
            assets = TeraAsset.get_assets_for_user(user_id=args['id_user'])
        elif args['id_creator_service']:
            if args['id_creator_service'] not in user_access.get_accessible_services_ids():
                return gettext("Service access denied"), 403
            assets = TeraAsset.get_assets_created_by_service(service_id=args['id_creator_service'])
        elif args['id_creator_user']:
            if args['id_creator_user'] not in user_access.get_accessible_users_ids():
                return gettext("User access denied"), 403
            assets = TeraAsset.get_assets_created_by_user(user_id=args['id_creator_user'])
        elif args['id_creator_participant']:
            if args['id_creator_participant'] not in user_access.get_accessible_participants_ids():
                return gettext("Participant access denied"), 403
            assets = TeraAsset.get_assets_created_by_participant(participant_id=args['id_creator_participant'])
        elif args['id_creator_device']:
            if args['id_creator_device'] not in user_access.get_accessible_devices_ids():
                return gettext("Device access denied"), 403
            assets = TeraAsset.get_assets_created_by_device(device_id=args['id_creator_device'])
        elif args['id_asset']:
            assets = user_access.query_asset(asset_id=args['id_asset'])
        elif args['asset_uuid']:
            assets = user_access.query_asset(asset_uuid=args['asset_uuid'])
        elif args['service_uuid']:
            assets = user_access.query_assets_associated_to_service(args['service_uuid'])
        else:
            return gettext('Missing argument'), 400
          
        if not assets:
            return []

        assets_list = []
        access_token = None
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']
        services_infos = []
        if (args['with_urls'] or args['with_only_token']) and assets:
            # services_infos = {service.service_uuid: service.service_clientendpoint
            #                   for service in user_access.get_accessible_services()}
            # Load all enabled services
            services_infos = {service.service_uuid: service.service_clientendpoint
                              for service in TeraService.query_with_filters({'service_enabled': True})}

            # # Access token
            # from opentera.redis.RedisVars import RedisVars
            # token_key = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
            # access_token = TeraAsset.get_access_token(asset_uuids=[asset.asset_uuid for asset in assets],
            #                                           token_key=token_key, requester_uuid=current_user.user_uuid,
            #                                           expiration=1800)
            # if args['with_only_token']:
            #     return {'access_token': access_token}

        for asset in assets:
            if args['with_only_token']:
                asset_json = {'asset_uuid': asset.asset_uuid}
            else:
                asset_json = asset.to_json(minimal=not args['full'])

            # Access token
            if args['with_urls'] or args['with_only_token']:
                # Access token
                token_key = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
                access_token = TeraAsset.get_access_token(asset_uuids=asset.asset_uuid,
                                                          token_key=token_key,
                                                          requester_uuid=current_user.user_uuid,
                                                          expiration=1800)
                asset_json['access_token'] = access_token

            if args['with_urls']:
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

            assets_list.append(asset_json)

        # if access_token:
        #     return {'access_token': access_token, 'assets': assets_list}
        # else:
        return assets_list

    @api.doc(description='Delete asset.',
             responses={501: 'Unable to update asset information from here'})
    @user_multi_auth.login_required
    def post(self):
        return gettext('Asset information update and creation must be done directly into a service (such as '
                       'Filetransfer service)'), 501

    @api.doc(description='Delete asset.',
             responses={501: 'Unable to delete asset information from here'})
    @user_multi_auth.login_required
    def delete(self):
        return gettext('Asset information deletion must be done directly into a service (such as '
                       'Filetransfer service)'), 501
