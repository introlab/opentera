import os
import hashlib
from datetime import datetime

import jwt
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


class QueryAssetFile(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.parser = reqparse.RequestParser()

    @api.expect(get_parser, validate=True)
    @api.doc(description='Download asset',
             responses={200: 'Success - start download!',
                        400: 'Bad request',
                        403: 'Access denied to the requested asset'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def get(self):
        args = get_parser.parse_args()

        try:
            access_token = jwt.decode(args['access_token'], ServiceAccessManager.api_service_token_key,
                                      algorithms='HS256')
        except jwt.PyJWTError:
            return gettext('Invalid access token'), 403

        if 'asset_uuids' not in access_token:
            return gettext('Invalid access token'), 403

        if args['asset_uuid'] not in access_token['asset_uuids']:
            return gettext('Forbidden'), 403

        # Ok, all is fine, we can provide the requested file
        asset = AssetFileData.get_asset_for_uuid(uuid_asset=args['asset_uuid'])

        src_dir = flask_app.config['UPLOAD_FOLDER']

        filename = asset.asset_original_filename
        return send_file(src_dir + '/' + str(asset.asset_uuid), as_attachment=True, attachment_filename=filename)

    @api.doc(description='Upload a new file asset to the service',
             responses={200: 'Success - Return informations about file assets',
                        400: 'Required parameter is missing',
                        403: 'Access denied to the requested asset'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def post(self):
        if not request.content_type.__contains__('multipart/form-data'):
            return gettext('Wrong content type'), 400

        if 'file_asset' not in request.files:
            return gettext('Missing file asset information'), 400

        if 'file' not in request.files:
            return gettext('Missing uploaded file'), 400

        file = request.files['file']

        if 'filename' not in file:
            return gettext('Missing filename'), 400

        # Check for required assets field
        try:
            asset_json = json.loads(request.files['file_asset'])
        except json.JSONDecodeError as err:
            return gettext('Invalid file_asset format'), 400

        if 'id_session' not in asset_json or 'asset_name' not in asset_json or 'asset_type' not in asset_json:
            return gettext('Missing required field(s) in asset descriptor'), 400

        # Check if session is accessible for the requester
        response = None
        if current_login_type == LoginType.USER_LOGIN:
            response = current_user_client.do_get_request_to_backend('/api/user/sessions&id_session=' +
                                                                     str(asset_json['id_session']))
        if current_login_type == LoginType.PARTICIPANT_LOGIN:
            response = current_participant_client.do_get_request_to_backend('/api/participant/sessions&id_session=' +
                                                                            str(asset_json['id_session']))
        if current_login_type == LoginType.DEVICE_LOGIN:
            response = current_device_client.do_get_request_to_backend('/api/device/sessions&id_session=' +
                                                                       str(asset_json['id_session']))
        if current_login_type == LoginType.SERVICE_LOGIN:
            response = current_service_client.do_get_request_to_backend('/api/service/sessions&id_session=' +
                                                                        str(asset_json['id_session']))

        if not response or response.status_code != 200:
            return gettext('Session access is forbidden'), 403

        # Manage id creator. Currently, only services can specify creators manually. Others are defined to the current
        # value
        if current_login_type == LoginType.SERVICE_LOGIN:
            if 'id_device' not in asset_json and 'id_participant' not in asset_json \
                    and 'id_user' not in asset_json and 'id_service' not in asset_json:
                return gettext('Missing at least one ID creator'), 400
        else:
            # Remove all present ids
            asset_json.pop('id_device')
            asset_json.pop('id_participant')
            asset_json.pop('id_user')
            asset_json.pop('id_service')
            if current_login_type == LoginType.USER_LOGIN:
                asset_json['id_user'] = current_user_client.id_user
            if current_login_type == LoginType.PARTICIPANT_LOGIN:
                asset_json['id_participant'] = current_participant_client.id_participant
            if current_login_type == LoginType.DEVICE_LOGIN:
                asset_json['id_device'] = current_device_client.id_device

        # Set asset managed to this service
        asset_json['asset_service_uuid'] = Globals.service.service_info['service_uuid']

        # Set asset datetime to current if not specified
        if 'asset_datetime' not in asset_json:
            asset_json['asset_datetime'] = datetime.now().isoformat()

        # OK, all set! Do the asset creation request...
        response = Globals.service.post_to_opentera('/api/services/assets', asset_json)
        if response.status_code != 200:
            return gettext('Unable to create asset') + ': ' + response.text, response.status_code

        # Create the asset in the local database
        try:
            new_asset_json = json.loads(response.json)
        except json.JSONDecodeError:
            return gettext('Unable to parse created asset'), 500

        asset_uuid = new_asset_json['asset_uuid']

        asset_file = AssetFileData()
        asset_file.asset_uuid = asset_uuid
        asset_file.asset_original_filename = secure_filename(file.filename)
        asset_file.asset_file_size = file.stream.tell()
        AssetFileData.insert(asset_file)

        # Finally... save the file itself!
        import os
        filename = os.path.join(flask_app.config['UPLOAD_FOLDER'], asset_uuid)
        with open(filename, 'wb') as fo:
            chunk = 8192
            while not request.stream.is_exhausted:
                fo.write(request.stream.read(chunk))

        # All done here - return asset info, including AssetFileData
        return new_asset_json.update(asset_file.to_json())

        #
        # if not args['asset_uuid']:
        #     return 'No asset_uuid specified', 400
        #
        # # Verify headers
        # if request.content_type == 'application/octet-stream':
        #     if 'X-Filename' not in request.headers:
        #         return 'No file specified', 400
        #
        #     # Save file on disk
        #     # TODO - Create another uuid for asset for filename?
        #     # TODO - Handle write errors
        #     fo = open(os.path.join(flask_app.config['UPLOAD_FOLDER'], args['asset_uuid'], "wb"))
        #     fo.write(request.data)
        #     fo.close()
        #
        #     # Create DB entry
        #     file_asset = AssetFileData()
        #     file_asset.asset_uuid = args['asset_uuid']
        #     file_asset.asset_creator_service_uuid = current_service_client.service_uuid
        #     file_asset.asset_original_filename = secure_filename(request.headers['X-Filename'])
        #     file_asset.asset_file_size = len(request.data)
        #     file_asset.asset_saved_date = datetime.now()
        #     file_asset.asset_md5 = hashlib.md5(request.data).hexdigest()
        #     db.session.add(file_asset)
        #     db.commit()
        #
        #     return file_asset.to_json()
        # elif request.content_type.__contains__('multipart/form-data'):
        #     # TODO should have only one file
        #     # check if the post request has the file part
        #     if 'file' not in request.files:
        #         return 'No file specified', 400
        #
        #     file = request.files['file']
        #
        #     # if user does not select file, browser also
        #     # submit an empty part without filename
        #     if file.filename == '':
        #         return 'No filename specified', 400
        #
        #     if file:
        #         filename = secure_filename(file.filename)
        #
        #         # Saving file
        #         file.save(os.path.join(flask_app.config['UPLOAD_FOLDER'], args['asset_uuid']))
        #         file_size = file.stream.tell()
        #
        #         # Reset stream
        #         file.stream.seek(0)
        #
        #         # Create DB entry
        #         file_asset = AssetFileData()
        #         file_asset.asset_uuid = args['asset_uuid']
        #         file_asset.asset_creator_service_uuid = current_service_client.service_uuid
        #         file_asset.asset_original_filename = filename
        #         file_asset.asset_file_size = file_size
        #         file_asset.asset_saved_date = datetime.now()
        #         # TODO avoid using a lot of RAM for md5?
        #         file_asset.asset_md5 = hashlib.md5(file.stream.read()).hexdigest()
        #         db.session.add(file_asset)
        #         db.session.commit()
        #         file.close()
        #
        #         return file_asset.to_json()
        #
        # return 'Unauthorized (invalid content type)', 403
