from flask import session, request
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraAsset import TeraAsset, AssetType
from libtera.db.models.TeraService import TeraService
from werkzeug.utils import secure_filename

from sqlalchemy import exc
from modules.DatabaseModule.DBManager import DBManager
from modules.RedisVars import RedisVars

import uuid

# Parser definition(s)
# GET
get_parser = api.parser()
get_parser.add_argument('id_asset', type=int, help='Specific ID of asset to query information.')
get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all assets')
get_parser.add_argument('id_session', type=int, help='ID of session from which to request all assets')
get_parser.add_argument('id_participant', type=int, help='ID of participant from which to request all assets')
get_parser.add_argument('service_uuid', type=str, help='Service UUID from which to request all assets')
get_parser.add_argument('all', type=str, help='return all assets accessible from user')

# POST
post_parser = api.parser()
post_parser.add_argument('id_session', type=int, help='ID of session to add the assets')

# DELETE
delete_parser = api.parser()
delete_parser.add_argument('id', type=int, help='Specific asset ID to delete', required=True)


class UserQueryAssets(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get asset information. Only one of the ID parameter is supported at once',
             responses={200: 'Success - returns list of assets',
                        400: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = get_parser.parse_args()

        # If we have no arguments, return all assets
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
        elif args['id_asset']:
            assets = [TeraAsset.get_asset_by_id(args['id_asset'])]
            if assets[0] is not None:
                if assets[0].id_device is not None and assets[0].id_device not in \
                        user_access.get_accessible_devices_ids():
                    return gettext('Permission denied'), 403
                if not user_access.query_session(session_id=assets[0].id_session):
                    return gettext('Permission denied'), 403
        elif args['service_uuid']:
            assets = user_access.query_assets_for_service(args['service_uuid'])
        elif args['all']:
            # TODO is 'all' useful
            assets = []

        assets_list = []
        for asset in assets:
            asset_json = asset.to_json()

            # TODO ADD ASSET URL
            # We have previously verified that the service is available to the user
            from libtera.db.models.TeraService import TeraService
            service = TeraService.get_service_by_uuid(asset.asset_service_uuid)

            servername = self.module.config.server_config['hostname']
            port = self.module.config.server_config['port']
            if 'X_EXTERNALHOST' in request.headers:
                if ':' in request.headers['X_EXTERNALHOST']:
                    servername, port = request.headers['X_EXTERNALHOST'].split(':', 1)
                else:
                    servername = request.headers['X_EXTERNALHOST']

            if 'X_EXTERNALPORT' in request.headers:
                port = request.headers['X_EXTERNALPORT']

            asset_json['asset_url'] = 'https://' + servername + ':' + str(port) \
                                      + service.service_clientendpoint \
                                      + 'api/file/assets?asset_uuid=' + asset.asset_uuid

            assets_list.append(asset_json)

        return assets_list

    @user_multi_auth.login_required
    @api.doc(description='Delete asset.',
             responses={200: 'Success - asset deleted',
                        500: 'Database error occurred',
                        403: 'Logged user doesn\'t have permission to delete the requested asset (must be an user of'
                             'the related project)'})
    @api.expect(delete_parser)
    def delete(self):
        from libtera.db.models.TeraSession import TeraSession
        from libtera.db.models.TeraParticipant import TeraParticipant
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Get data in itself to validate we can delete it
        asset = TeraAsset.get_asset_by_id(id_todel)

        # Get accessible projects list
        projects_ids = user_access.get_accessible_participants_ids()

        # Check if current user can delete
        if len(TeraAsset.query.join(TeraSession).join(TeraSession.session_participants).filter(
                TeraParticipant.id_project.in_(projects_ids)).all()) == 0:
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraAsset.delete(id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryAssets.__name__,
                                         'get', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200

    @user_multi_auth.login_required
    @api.doc(description='Post asset.',
             responses={200: 'Success - asset posted',
                        500: 'Database error occurred',
                        403: 'Logged user doesn\'t have permission to delete the requested asset (must be an user of'
                             'the related project)'})
    @api.expect(post_parser)
    def post(self):
        # TODO What to do here exactly?
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        args = post_parser.parse_args()

        # Verify if user can access session
        session_ids = user_access.get_accessible_sessions_ids()

        if args['id_session'] in session_ids:

            created_assets = []

            for file in request.files:
                storage = request.files[file]
                filename = secure_filename(storage.filename)

                # TODO Asset associated with FileTransferService?
                service = TeraService.get_service_by_key('FileTransferService')

                # Create asset
                new_asset = TeraAsset()
                new_asset.asset_name = filename
                # TODO HARDCODED ASSET TYPE FOR NOW
                new_asset.asset_type = AssetType.RAW_FILE.value
                new_asset.id_session = args['id_session']
                # TODO Asset associated to us
                new_asset.id_user = current_user.id_user
                # TeraServer service_uuid
                new_asset.asset_service_uuid = service.service_uuid
                TeraAsset.insert(new_asset)

                # Upload to FileTransferService
                tera_service = TeraService.get_openteraserver_service()
                token = tera_service.get_token(self.module.redis.get(RedisVars.RedisVar_ServiceTokenAPIKey))
                params = {'asset_uuid': new_asset.asset_uuid}
                request_headers = {'Authorization': 'OpenTera ' + token}
                from requests import post
                import io
                # TODO AVOID USING RAM?
                f = io.BytesIO(storage.stream.read())
                files = {'file': (filename, f)}
                url = 'http://' + service.service_hostname + ':' + str(service.service_port) + '/api/file/assets'
                response = post(url=url, files=files, params=params, headers=request_headers)
                storage.close()
                f.close()

                if response.status_code == 200:
                    # Success!
                    asset_json = new_asset.to_json()
                    asset_json['asset_data'] = response.json()
                    return asset_json
                else:
                    # Remove asset, was not able to upload
                    TeraAsset.delete(new_asset.id_asset)
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryAssets.__name__,
                                                 'post', 500, 'Error uploading file(s)', files)
                    return gettext('Error uploading file'), 500
        return gettext('Not authorized'), 403
