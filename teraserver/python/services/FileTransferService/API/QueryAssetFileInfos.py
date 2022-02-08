import jwt
from flask import request
from flask_babel import gettext
from flask_restx import Resource, reqparse
from services.FileTransferService.FlaskModule import file_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_service_client, current_login_type, \
    current_user_client, current_device_client
from services.FileTransferService.libfiletransferservice.db.models.AssetFileData import AssetFileData
import services.FileTransferService.Globals as Globals

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('access_token', type=str, required=True, help='Access token proving that the requested assets '
                                                                      'can be accessed.')
get_parser.add_argument('asset_uuid', type=str, required=True, help='UUID of the asset to get info')

# post_schema = api.schema_model('assets_uuids', {'properties': {
#                                                                 'assets_uuids': {
#                                                                     'type': 'array',
#                                                                     'location': 'json'}
#                                                                 },
#                                                 },
#                                'file_asset', {'properties': AssetFileData.get_json_schema(),
#                                               'type': 'object',
#                                               'location': 'json'},
#                                'access_token', {'properties': {
#                                                                 'access_token': {
#                                                                     'type': 'string',
#                                                                     'location': 'json'}
#                                                                 },
#                                                 }
#                                )
post_schema = api.schema_model('assets_uuids', {'properties': {
                                                                'assets_uuids': {
                                                                    'type': 'array',
                                                                    'location': 'json'}
                                                                },
                                                }
                               )


class QueryAssetFileInfos(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.parser = reqparse.RequestParser()

    @api.expect(get_parser, validate=True)
    @api.doc(description='Query informations about stored file',
             responses={200: 'Success - Return informations about file',
                        400: 'Bad request',
                        403: 'Access denied to the requested asset'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def get(self):
        args = get_parser.parse_args()

        if not Globals.service.has_access_to_asset(args['access_token'], args['asset_uuid']):
            return gettext('Access denied for that asset'), 403

        # Ok, all is fine, we can provide the requested information
        asset = AssetFileData.get_asset_for_uuid(uuid_asset=args['asset_uuid'])

        if not asset:
            return gettext('No asset found'), 400

        return asset.to_json()

    @api.expect(post_schema)
    @api.doc(description='Query information about multiple assets at the same time or update an existing asset '
                         'information. If the \'asset_uuids\' list is present in the data, return assets. Otherwise, '
                         'uses the \'file_asset\' informations to update the data',
             responses={200: 'Success - Return informations about file assets',
                        400: 'Required parameter is missing',
                        403: 'Access denied to the requested asset'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def post(self):
        if 'access_token' not in request.json:
            return gettext('Missing access token'), 403

        if 'asset_uuids' not in request.json and 'file_asset' not in request.json:
            return gettext('Badly formatted request'), 400

        allowed_asset_uuids = Globals.service.get_accessible_asset_uuids(request.json['access_token'])

        if 'asset_uuids' in request.json:
            # Query assets data
            requested_assets_uuids = request.json['asset_uuids']
            if list(set(requested_assets_uuids) - set(allowed_asset_uuids)):
                # At least one id was requested but not allowed
                return gettext('Access denied for at least one requested asset'), 403

            assets = AssetFileData.get_assets_for_uuids(requested_assets_uuids)

            return [asset.to_json() for asset in assets]
        else:
            # Update file asset
            asset_json = request.json['file_asset']
            if 'asset_uuid' not in asset_json:
                return gettext('Missing asset uuid'), 400

            if asset_json['asset_uuid'] not in allowed_asset_uuids:
                return gettext('Forbidden'), 403

            # Only change possible here is the original file name, as other information are linked to the file itself
            if 'asset_original_filename' not in asset_json:
                return gettext('Only original filename can be changed from here'), 400

            asset = AssetFileData.get_asset_for_uuid(asset_json['asset_uuid'])

            if not asset:
                return gettext('Unknown asset'), 400

            asset.asset_original_filename = asset_json['asset_original_filename']
            asset.commit()

            return asset.to_json()

        # args = post_parser.parse_args()
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
