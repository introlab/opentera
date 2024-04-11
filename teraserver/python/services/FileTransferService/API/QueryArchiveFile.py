import os
from datetime import datetime
import json
from werkzeug.utils import secure_filename
from flask import request, send_file
from flask_babel import gettext
from flask_restx import Resource
from services.FileTransferService.FlaskModule import file_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_service_client, \
    current_login_type, current_user_client, current_device_client, current_participant_client, LoginType
from services.FileTransferService.FlaskModule import flask_app
from services.FileTransferService.libfiletransferservice.db.models.ArchiveFileData import ArchiveFileData
import services.FileTransferService.Globals as Globals

# Parser definition(s)
get_parser = api.parser()

get_parser.add_argument('archive_uuid', type=str, required=True, help='UUID of the asset to download')

delete_parser = api.parser()
delete_parser.add_argument('uuid', type=str, required=True, help='UUID of the archive do delete')


class QueryArchiveFile(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.expect(get_parser, validate=True)
    @api.doc(description='Download archive',
             responses={200: 'Success - start download!',
                        400: 'Bad request',
                        403: 'Access denied to the requested asset'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def get(self):
        args = get_parser.parse_args()

        # TODO verify permissions
        archive = ArchiveFileData.get_archive_by_uuid(args['archive_uuid'])
        if archive is None:
            return gettext('No archive found'), 404

        src_dir = flask_app.config['UPLOAD_FOLDER']

        filename = archive.archive_original_filename
        return send_file(src_dir + '/' + str(archive.archive_uuid), as_attachment=True, download_name=filename)

    @api.doc(description='Upload a new file archive to the service',
             responses={200: 'Success - Return information about archive',
                        400: 'Required parameter is missing',
                        403: 'Access denied to the requested asset'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=True)
    def post(self):
        if not request.content_type.__contains__('multipart/form-data'):
            return gettext('Wrong content type'), 400

        if 'file_archive' not in request.form:
            return gettext('Missing file archive information'), 400

        if 'file' not in request.files:
            return gettext('Missing uploaded file'), 400

        file = request.files['file']

        if not file.filename:
            return gettext('Missing filename'), 400

        return gettext("Not implemented"), 501

    @api.expect(delete_parser, validate=True)
    @api.doc(description='Delete archive',
             responses={200: 'Success - archive deleted',
                        400: 'Bad request',
                        403: 'Access denied to the requested archive'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def delete(self):
        parser = delete_parser

        args = parser.parse_args()
        uuid_todel = args['uuid']

        # TODO Verify permissions

        # Delete from OpenTera Server
        archive = ArchiveFileData.get_archive_by_uuid(uuid_todel)
        if archive is None:
            return gettext('No archive found'), 404

        archive.delete_file_archive(flask_app.config['UPLOAD_FOLDER'])
        return gettext('Archive deleted'), 200
