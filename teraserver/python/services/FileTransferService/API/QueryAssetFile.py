import os
from datetime import datetime

import json
from werkzeug.utils import secure_filename
from flask import request, send_file
from flask_babel import gettext
from flask_restx import Resource, reqparse
from services.FileTransferService.FlaskModule import file_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_service_client, \
    current_login_type, current_user_client, current_device_client, current_participant_client, LoginType
from services.FileTransferService.FlaskModule import flask_app
from services.FileTransferService.libfiletransferservice.db.models.AssetFileData import AssetFileData

import services.FileTransferService.Globals as Globals

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('access_token', type=str, required=True, help='Access token proving that the requested assets '
                                                                      'can be accessed.')
get_parser.add_argument('asset_uuid', type=str, required=True, help='UUID of the asset to download')

delete_parser = api.parser()
delete_parser.add_argument('uuid', type=str, help='UUID of the asset do delete')
delete_parser.add_argument('access_token', type=str, required=True, help='Access token proving that the requested '
                                                                         'asset can be deleted.')


class QueryAssetFile(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.expect(get_parser, validate=True)
    @api.doc(description='Download asset',
             responses={200: 'Success - start download!',
                        400: 'Bad request',
                        403: 'Access denied to the requested asset'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def get(self):
        args = get_parser.parse_args()

        if not Globals.service.has_access_to_asset(args['access_token'], args['asset_uuid']):
            return gettext('Access denied to asset'), 403

        # Ok, all is fine, we can provide the requested file
        asset = AssetFileData.get_asset_for_uuid(uuid_asset=args['asset_uuid'])
        if asset is None:
            return gettext('No asset found'), 404

        src_dir = flask_app.config['UPLOAD_FOLDER']

        filename = asset.asset_original_filename
        return send_file(src_dir + '/' + str(asset.asset_uuid), as_attachment=True, download_name=filename)

    @api.doc(description='Upload a new file asset to the service',
             responses={200: 'Success - Return informations about file assets',
                        400: 'Required parameter is missing',
                        403: 'Access denied to the requested asset'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def post(self):
        if not request.content_type.__contains__('multipart/form-data'):
            return gettext('Wrong content type'), 400

        if 'file_asset' not in request.form:
            return gettext('Missing file asset information'), 400

        if 'file' not in request.files:
            return gettext('Missing uploaded file'), 400

        file = request.files['file']

        if not file.filename:
            return gettext('Missing filename'), 400

        # Check for required assets field
        try:
            asset_json = json.loads(request.form['file_asset'])
        except json.JSONDecodeError as err:
            return gettext('Invalid file_asset format'), 400

        if 'id_session' not in asset_json or 'asset_name' not in asset_json:
            return gettext('Missing required field(s) in asset descriptor'), 400

        # Check if session is accessible for the requester
        if current_login_type == LoginType.SERVICE_LOGIN:
            response = current_service_client.do_get_request_to_backend('/api/service/sessions?id_session=' +
                                                                        str(asset_json['id_session']))
        else:
            response = Globals.service.get_from_opentera('/api/service/sessions',
                                                         {'id_session': asset_json['id_session']})

        if not response or response.status_code != 200 or not response.json():
            return gettext('Session access is forbidden'), 403

        session_json = response.json()[0]
        if current_login_type == LoginType.USER_LOGIN:
            if not current_user_client.user_superadmin:
                access_allowed = False
                # Project admins are always allowed to add files to any session
                if 'session_participants' in session_json:
                    if len(session_json['session_participants']) > 0:
                        id_project = session_json['session_participants'][0]['id_project']
                        if current_user_client.get_role_for_project(id_project=id_project) == 'admin':
                            access_allowed = True

                if not access_allowed:
                    if not 'session_users' not in session_json or (
                            current_user_client.user_uuid not in
                            [user['user_uuid'] for user in session_json['session_users']]
                            and current_user_client.id_user != session_json['id_creator_user']):
                        access_allowed = True
                if not access_allowed:
                    return gettext('Session access is forbidden'), 403

        if current_login_type == LoginType.DEVICE_LOGIN:
            if 'session_devices' not in session_json or (
                    current_device_client.device_uuid not in
                    [device['device_uuid'] for device in session_json['session_devices']]
                    and current_device_client.id_device != session_json['id_creator_device']):
                return gettext('Session access is forbidden'), 403

        if current_login_type == LoginType.PARTICIPANT_LOGIN:
            if 'session_participants' not in session_json or (
                    current_participant_client.participant_uuid not in
                    [part['participant_uuid'] for part in session_json['session_participants']]
                    and current_participant_client.id_participant != session_json['id_creator_participant']):
                return gettext('Session access is forbidden'), 403

        # Manage id creator. Currently, only services can specify creators manually. Others are defined to the current
        # value
        if current_login_type == LoginType.SERVICE_LOGIN:
            if 'id_device' not in asset_json and 'id_participant' not in asset_json \
                    and 'id_user' not in asset_json and 'id_service' not in asset_json:
                return gettext('Missing at least one ID creator'), 400
            asset_json['id_service'] = current_service_client.get_service_infos()['id_service']
        else:
            # Prevent creating an asset for someone else
            if current_login_type == LoginType.USER_LOGIN:
                asset_json['id_user'] = current_user_client.id_user
            if current_login_type == LoginType.PARTICIPANT_LOGIN:
                asset_json['id_participant'] = current_participant_client.id_participant
            if current_login_type == LoginType.DEVICE_LOGIN:
                asset_json['id_device'] = current_device_client.id_device

        # Set asset managed to this service
        asset_json['asset_service_uuid'] = Globals.service.service_info['service_uuid']

        # Set asset type if missing
        original_filename = secure_filename(file.filename)
        if 'asset_type' not in asset_json:
            # Set the asset type based on the filename
            import mimetypes
            mime = mimetypes.guess_type(original_filename)[0]
            if mime:
                asset_json['asset_type'] = mime
            else:
                asset_json['asset_type'] = 'application/octet-stream'  # General content type, unknown

        # Set asset datetime to current if not specified
        if 'asset_datetime' not in asset_json:
            asset_json['asset_datetime'] = datetime.now().isoformat()

        # OK, all set! Do the asset creation request...
        asset_json['id_asset'] = 0  # New asset creation
        response = Globals.service.post_to_opentera('/api/service/assets', {'asset': asset_json})
        if response.status_code != 200:
            return gettext('Unable to create asset') + ': ' + response.text, response.status_code

        # Create the asset in the local database
        new_asset_json = response.json()[0]
        asset_uuid = new_asset_json['asset_uuid']

        filename = os.path.join(flask_app.config['UPLOAD_FOLDER'], asset_uuid)

        file_size = file.content_length
        if file_size == 0:
            # No specified content length - find the file size manually
            file_size = file.seek(0, os.SEEK_END)
            file.seek(0)

        asset_file = AssetFileData()
        asset_file.asset_uuid = asset_uuid
        asset_file.asset_original_filename = original_filename
        asset_file.asset_file_size = file_size
        AssetFileData.insert(asset_file)

        # Finally... save the file itself!
        file.save(filename)

        # All done here - return asset info, including AssetFileData
        full_json = {**new_asset_json, **asset_file.to_json()}

        # Create asset infos + download url
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']
        else:
            servername = self.module.config.service_config['hostname']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']
        else:
            port = self.module.config.service_config['port']

        endpoint = Globals.service.service_info['service_clientendpoint']
        # Access token
        from opentera.redis.RedisVars import RedisVars
        from opentera.db.models.TeraAsset import TeraAsset
        token_key = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
        access_token = TeraAsset.get_access_token(asset_uuids=[asset_uuid], token_key=token_key,
                                                  requester_uuid=Globals.service.get_current_requester_uuid(),
                                                  expiration=1800)

        full_json['asset_infos_url'] = 'https://' + servername + ':' + str(port) + endpoint\
                                       + '/api/assets/infos'  # ?asset_uuid=' + asset_uuid
        full_json['asset_url'] = 'https://' + servername + ':' + str(port) + endpoint\
                                 + '/api/assets'  # ?asset_uuid=' + asset_uuid
        full_json['access_token'] = access_token
        return full_json

    @api.expect(delete_parser, validate=True)
    @api.doc(description='Delete asset',
             responses={200: 'Success - asset deleted',
                        400: 'Bad request',
                        403: 'Access denied to the requested asset'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def delete(self):
        parser = delete_parser

        args = parser.parse_args()
        uuid_todel = args['uuid']

        if not Globals.service.has_access_to_asset(args['access_token'], uuid_todel):
            return gettext('Access denied to asset'), 403

        # Delete from OpenTera Server
        response = Globals.service.delete_from_opentera('/api/service/assets', {'uuid': uuid_todel})
        if response.status_code != 200:
            return gettext('Unable to delete asset') + ': ' + response.text, response.status_code

        return '', 200
