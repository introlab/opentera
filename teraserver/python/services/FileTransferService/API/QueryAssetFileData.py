import os
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import request
from flask_restx import Resource, reqparse
from services.FileTransferService.FlaskModule import file_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_service_client
from services.FileTransferService.FlaskModule import flask_app
from services.FileTransferService.libfiletransferservice.db.models.AssetFileData import AssetFileData
from services.FileTransferService.libfiletransferservice.db.Base import db

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('asset_uuid', type=str, help='UUID of the asset')

post_parser = api.parser()
post_parser.add_argument('asset_uuid', type=str, help='UUID of the asset')


class QueryAssetFileData(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.parser = reqparse.RequestParser()

    @api.expect(get_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @ServiceAccessManager.service_token_required
    def get(self):
        print('OK!')
        args = get_parser.parse_args()
        return 'Unauthorized', 403

    @api.expect(post_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @ServiceAccessManager.service_token_required
    def post(self):
        print('OK!')
        args = post_parser.parse_args()

        if not args['asset_uuid']:
            return 'No asset_uuid specified', 400

        # Verify headers
        if request.content_type == 'application/octet-stream':
            if 'X-Filename' not in request.headers:
                return 'No file specified', 400

            # Save file on disk
            # TODO - Create another uuid for asset for filename?
            # TODO - Handle write errors
            fo = open(os.path.join(flask_app.config['UPLOAD_FOLDER'], args['asset_uuid'], "wb"))
            fo.write(request.data)
            fo.close()

            # Create DB entry
            file_asset = AssetFileData()
            file_asset.asset_uuid = args['asset_uuid']
            file_asset.asset_creator_service_uuid = current_service_client.service_uuid
            file_asset.asset_original_filename = secure_filename(request.headers['X-Filename'])
            file_asset.asset_file_size = len(request.data)
            file_asset.asset_saved_date = datetime.now()
            file_asset.asset_md5 = hashlib.md5(request.data).hexdigest()
            db.session.add(file_asset)
            db.commit()

            return file_asset.to_json()
        elif request.content_type.__contains__('multipart/form-data'):
            # TODO should have only one file
            # check if the post request has the file part
            if 'file' not in request.files:
                return 'No file specified', 400

            file = request.files['file']

            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                return 'No filename specified', 400

            if file:
                filename = secure_filename(file.filename)

                # Saving file
                file.save(os.path.join(flask_app.config['UPLOAD_FOLDER'], args['asset_uuid']))
                file_size = file.stream.tell()

                # Reset stream
                file.stream.seek(0)

                # Create DB entry
                file_asset = AssetFileData()
                file_asset.asset_uuid = args['asset_uuid']
                file_asset.asset_creator_service_uuid = current_service_client.service_uuid
                file_asset.asset_original_filename = filename
                file_asset.asset_file_size = file_size
                file_asset.asset_saved_date = datetime.now()
                # TODO avoid using a lot of RAM for md5?
                file_asset.asset_md5 = hashlib.md5(file.stream.read()).hexdigest()
                db.session.add(file_asset)
                db.session.commit()
                file.close()

                return file_asset.to_json()

        return 'Unauthorized (invalid content type)', 403
