from flask import request
from flask_restx import Resource, reqparse
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from opentera.db.models.TeraAsset import TeraAsset, AssetType
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy import exc


# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_asset', type=int, help='Specific ID of asset to query information.')
get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all assets')
get_parser.add_argument('id_session', type=int, help='ID of session from which to request all assets')
get_parser.add_argument('id_participant', type=int, help='ID of participant from which to request all assets')

post_parser = api.parser()

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Site ID to delete', required=True)


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
        if not any(args.values()):
            return gettext('Missing arguments'), 400
        elif args['id_device']:
            if args['id_device'] not in service_access.get_accessible_devices_ids():
                return gettext('Device access denied'), 403
            assets = TeraAsset.get_assets_for_device(device_id=args['id_device'])
        elif args['id_session']:
            if not args['id_session'] in service_access.get_accessible_sessions_ids():
                return gettext('Session access denied'), 403
            assets = TeraAsset.get_assets_for_session(session_id=args['id_session'])
        elif args['id_participant']:
            if args['id_participant'] not in service_access.get_accessible_participants_ids():
                return gettext('Participant access denied'), 403
            assets = TeraAsset.get_assets_for_participant(part_id=args['id_participant'])
        elif args['id_asset']:
            assets = [TeraAsset.get_asset_by_id(args['id_asset'])]
            if assets[0] is not None:
                if assets[0].id_device is not None and assets[0].id_device not in \
                        service_access.get_accessible_devices_ids():
                    return gettext('Permission denied'), 403
                if not assets[0].id_session in service_access.get_accessible_sessions_ids():
                    return gettext('Permission denied'), 403

        assets_list = []
        for asset in assets:
            asset_json = asset.to_json()
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

        if 'id_session' in asset_info and asset_info['id_session'] < 1:
            return gettext('Unknown session'), 400

        if 'asset_name' in asset_info and not asset_info['asset_name']:
            return gettext('Invalid asset name'), 400

        if 'asset_type' in asset_info and not asset_info['asset_type'] \
                                              in [asset_type.value for asset_type in AssetType]:
            return gettext('Invalid asset type'), 400

        # Check if the service can create/update that asset
        if asset_info['id_asset'] != 0 and 'id_session' not in asset_info:
            # Updating asset - get asset and validate session asset
            asset = TeraAsset.get_asset_by_id(asset_info['id_asset'])
            if asset:
                args['id_session'] = asset.id_session

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

        # TODO: Publish update to everyone who is subscribed to assets updates
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
        id_todel = args['id']

        asset = TeraAsset.get_asset_by_id(id_todel)

        if not asset:
            return gettext('Missing arguments'), 400

        if asset.id_session not in service_access.get_accessible_sessions_ids(True):
            return gettext('Service can\'t delete assets for that session'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraAsset.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryAssets.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200

