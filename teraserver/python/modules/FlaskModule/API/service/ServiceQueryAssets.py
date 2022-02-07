from flask import request
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraService import TeraService
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy import exc


# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_asset', type=int, help='Specific ID of asset to query information.')
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

post_parser = api.parser()

delete_parser = api.parser()
delete_parser.add_argument('uuid', type=str, help='Asset UUID to delete', required=True)


class ServiceQueryAssets(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return assets information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged service doesn\'t have permission to access the requested data'})
    def get(self):
        service_access = DBManager.serviceAccess(current_service)

        args = get_parser.parse_args()

        # If we have no arguments, don't do anything!
        assets = []
        if not any(args.values()):
            return gettext('No arguments specified'), 400
        elif args['id_device']:
            if args['id_device'] not in service_access.get_accessible_devices_ids():
                return gettext('Device access denied'), 403
            assets = TeraAsset.get_assets_for_device(device_id=args['id_device'])
        elif args['id_session']:
            if args['id_session'] not in service_access.get_accessible_sessions_ids():
                return gettext('Session access denied'), 403
            assets = TeraAsset.get_assets_for_session(session_id=args['id_session'])
        elif args['id_participant']:
            if args['id_participant'] not in service_access.get_accessible_participants_ids():
                return gettext('Participant access denied'), 403
            assets = TeraAsset.get_assets_for_participant(part_id=args['id_participant'])
        elif args['id_user']:
            if args['id_user'] not in service_access.get_accessible_users_ids():
                return gettext("User access denied"), 403
            assets = TeraAsset.get_assets_for_user(user_id=args['id_user'])
        elif args['id_creator_service']:
            assets = TeraAsset.get_assets_created_by_service(service_id=args['id_creator_service'])
        elif args['id_creator_user']:
            if args['id_creator_user'] not in service_access.get_accessible_users_ids():
                return gettext("User access denie"), 403
            assets = TeraAsset.get_assets_created_by_user(user_id=args['id_creator_user'])
        elif args['id_creator_participant']:
            if args['id_creator_participant'] not in service_access.get_accessible_participants_ids():
                return gettext("Participant access denied"), 403
            assets = TeraAsset.get_assets_created_by_participant(participant_id=args['id_creator_participant'])
        elif args['id_creator_device']:
            if args['id_creator_device'] not in service_access.get_accessible_devices_ids():
                return gettext("Device access denied"), 403
            assets = TeraAsset.get_assets_created_by_device(device_id=args['id_creator_device'])
        elif args['id_asset']:
            assets = service_access.query_asset(args['id_asset'])
        elif args['service_uuid']:
            assets = TeraAsset.get_assets_owned_by_service(service_uuid=args['service_uuid'])
        else:
            return gettext('Missing argument'), 400

        assets_list = []
        access_token = None
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']
        services_infos = []
        if args['with_urls']:
            services_infos = {service.service_uuid: service.service_clientendpoint
                              for service in TeraService.query.filter(TeraService.service_enabled == True).all()}

            # Access token
            from opentera.redis.RedisVars import RedisVars
            token_key = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
            access_token = TeraAsset.get_access_token(asset_uuids=[asset.asset_uuid for asset in assets],
                                                      token_key=token_key, requester_uuid=current_service.service_uuid,
                                                      expiration=1800)

        for asset in assets:
            asset_json = asset.to_json()

            if args['with_urls']:
                if asset.asset_service_uuid in services_infos:
                    asset_json['asset_infos_url'] = 'https://' + servername + ':' + str(port) \
                                                    + services_infos[asset.asset_service_uuid] \
                                                    + '/api/assets/infos?asset_uuid=' + asset.asset_uuid
                    asset_json['asset_url'] = 'https://' + servername + ':' + str(port) \
                                              + services_infos[asset.asset_service_uuid] \
                                              + '/api/assets?asset_uuid=' + asset.asset_uuid

                    if not assets_list:
                        # Append access token to first item only
                        asset_json['access_token'] = access_token
                else:
                    # Service not found or unavaiable for current user
                    asset_json['asset_infos_url'] = None
                    asset_json['asset_url'] = None

            assets_list.append(asset_json)

        return assets_list

    @LoginModule.service_token_or_certificate_required
    # @api.expect(post_parser)
    @api.doc(description='Adds a new asset to the OpenTera database',
             responses={200: 'Success - asset correctly added',
                        400: 'Bad request - wrong or missing parameters in query',
                        500: 'Required parameter is missing',
                        403: 'Service doesn\'t have permission to post that asset'})
    def post(self):
        args = post_parser.parse_args()
        service_access = DBManager.serviceAccess(current_service)

        # Using request.json instead of parser, since parser messes up the json!
        if 'asset' not in request.json:
            return gettext('Missing asset field'), 400

        asset_info = request.json['asset']

        # All fields validation
        if 'id_asset' not in asset_info:
            return gettext('Missing id_asset field'), 400

        if asset_info['id_asset'] == 0:
            if 'id_session' not in asset_info:
                return gettext('Unknown session'), 400

            if 'asset_type' not in asset_info or ('asset_type' in asset_info and not asset_info['asset_type']):
                return gettext('Invalid asset type'), 400

        if 'asset_name' not in asset_info and not asset_info['asset_name']:
            return gettext('Invalid asset name'), 400

        # Check if the service can create/update that asset
        if asset_info['id_asset'] != 0 and 'id_session' not in asset_info:
            # Updating asset - get asset and validate session asset
            asset = TeraAsset.get_asset_by_id(asset_info['id_asset'])
            if asset:
                asset_info['id_session'] = asset.id_session

        if asset_info['id_session'] not in service_access.get_accessible_sessions_ids(True):
            return gettext('Service can\'t create assets for that session'), 403

        # Create a new asset?
        if asset_info['id_asset'] == 0:
            try:
                # Create asset
                new_asset = TeraAsset()
                new_asset.from_json(asset_info)
                # Prevent identity theft!
                new_asset.asset_service_uuid = current_service.service_uuid
                TeraAsset.insert(new_asset)
                # Update ID for further use
                asset_info['id_asset'] = new_asset.id_asset
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryAssets.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # Update asset
            try:
                if 'asset_service_uuid' in asset_info:
                    # Prevent identity theft!
                    asset_info['asset_service_uuid'] = current_service.service_uuid
                TeraAsset.update(asset_info['id_asset'], asset_info)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryAssets.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        update_asset = TeraAsset.get_asset_by_id(asset_info['id_asset'])

        return [update_asset.to_json()]

    @LoginModule.service_token_or_certificate_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific asset',
             responses={200: 'Success',
                        403: 'Service can\'t delete asset',
                        500: 'Database error.'})
    def delete(self):
        service_access = DBManager.serviceAccess(current_service)
        parser = delete_parser

        args = parser.parse_args()
        uuid_todel = args['uuid']

        asset = TeraAsset.get_asset_by_uuid(uuid_todel)

        if not asset:
            return gettext('Missing arguments'), 400

        if asset.id_session not in service_access.get_accessible_sessions_ids(True):
            return gettext('Service can\'t delete assets for that session'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraAsset.delete(id_todel=asset.id_asset)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryAssets.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200

