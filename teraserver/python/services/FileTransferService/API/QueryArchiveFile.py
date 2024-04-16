import os
from datetime import datetime
import json
from flask import request, send_file
from flask_babel import gettext
from flask_restx import Resource
from services.FileTransferService.FlaskModule import file_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_service_client, \
    current_login_type, current_user_client, current_device_client, current_participant_client, LoginType
from services.FileTransferService.FlaskModule import flask_app
from services.FileTransferService.libfiletransferservice.db.models.ArchiveFileData import ArchiveFileData
from services.FileTransferService.libfiletransferservice.db.models.ArchiveFileData import TeraArchiveStatus
from services.FileTransferService.API.send_archive_event import send_archive_event

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('archive_uuid', type=str, required=True, help='UUID of the archive to download')

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
                        403: 'Access denied to the requested archive'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def get(self):
        args = get_parser.parse_args()

        if current_login_type == LoginType.USER_LOGIN:
            requester_uuid = current_user_client.user_uuid
        elif current_login_type == LoginType.DEVICE_LOGIN:
            requester_uuid = current_device_client.device_uuid
        elif current_login_type == LoginType.PARTICIPANT_LOGIN:
            requester_uuid = current_participant_client.participant_uuid
        elif current_login_type == LoginType.SERVICE_LOGIN:
            requester_uuid = current_service_client.service_uuid
        else:
            requester_uuid = None

        # Verify if the archive exists
        archive = ArchiveFileData.get_archive_by_uuid(args['archive_uuid'])
        if archive is None:
            return gettext('No archive found'), 404

        # Verify ownership
        if archive.owner_uuid != requester_uuid:
            return gettext('Access denied to the requested archive'), 403

        src_dir = flask_app.config['UPLOAD_FOLDER']

        # Send file
        filename = archive.archive_original_filename
        return send_file(src_dir + '/' + str(archive.archive_uuid), as_attachment=True, download_name=filename)

    @api.doc(description='Upload a new file archive to the service',
             responses={200: 'Success - Return information about archive',
                        400: 'Required parameter is missing',
                        403: 'Access denied to the requested archive'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=True)
    def post(self):
        if current_login_type == LoginType.USER_LOGIN:
            uploader_uuid = current_user_client.user_uuid
        elif current_login_type == LoginType.DEVICE_LOGIN:
            uploader_uuid = current_device_client.device_uuid
        elif current_login_type == LoginType.PARTICIPANT_LOGIN:
            uploader_uuid = current_participant_client.participant_uuid
        elif current_login_type == LoginType.SERVICE_LOGIN:
            uploader_uuid = current_service_client.service_uuid
        else:
            uploader_uuid = None

        if not request.content_type.__contains__('multipart/form-data'):
            return gettext('Wrong content type'), 400

        if 'archive' not in request.form:
            return gettext('Missing archive information'), 400

        if 'file' not in request.files:
            return gettext('Missing uploaded file'), 400

        file = request.files['file']

        if not file.filename:
            return gettext('Missing filename'), 400

        # Get the archive information
        try:
            archive_info = json.loads(request.form['archive'])

            if 'id_archive_file_data' not in archive_info:
                return gettext('Missing archive ID'), 400

            archive = ArchiveFileData.get_archive_by_id(archive_info['id_archive_file_data'])
            if archive is None:
                return gettext('No archive found'), 404

            if archive.archive_status == TeraArchiveStatus.STATUS_COMPLETED.value:
                return gettext('Archive has already been uploaded.'), 404

            if archive.archive_original_filename != file.filename:
                return gettext('Filename does not match the archive information'), 400

            # Get the data from the post
            archive.archive_upload_datetime = datetime.now()
            archive.archive_uploader_uuid = uploader_uuid

            # Save the file
            file_size = file.content_length
            if file_size == 0:
                # No specified content length - find the file size manually
                file_size = file.seek(0, os.SEEK_END)
                file.seek(0)

            # Update file size
            archive.archive_file_size = file_size

            # Save filename = uuid
            filename = os.path.join(flask_app.config['UPLOAD_FOLDER'], archive.archive_uuid)
            # Save
            file.save(filename)

            # Update status
            archive.archive_status = TeraArchiveStatus.STATUS_COMPLETED.value

            # Update DB
            archive.commit()

            send_archive_event(archive)

            return archive.to_json()
        except Exception as e:
            return gettext('Error parsing archive information : ') + str(e), 400

        return gettext("Not implemented"), 501

    @api.expect(delete_parser, validate=True)
    @api.doc(description='Delete archive',
             responses={200: 'Success - archive deleted',
                        400: 'Bad request',
                        403: 'Access denied to the requested archive'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def delete(self):
        args = delete_parser.parse_args()
        uuid_todel = args['uuid']

        if current_login_type == LoginType.USER_LOGIN:
            deleter_uuid = current_user_client.user_uuid
        elif current_login_type == LoginType.DEVICE_LOGIN:
            deleter_uuid = current_device_client.device_uuid
        elif current_login_type == LoginType.PARTICIPANT_LOGIN:
            deleter_uuid = current_participant_client.participant_uuid
        elif current_login_type == LoginType.SERVICE_LOGIN:
            deleter_uuid = current_service_client.service_uuid
        else:
            deleter_uuid = None

        # Get archive
        archive = ArchiveFileData.get_archive_by_uuid(uuid_todel)
        if archive is None:
            return gettext('No archive found'), 404

        if deleter_uuid != archive.archive_owner_uuid and deleter_uuid != archive.archive_uploader_uuid:
            return gettext('Access denied to the requested archive'), 403

        # Delete archive
        archive_copy = ArchiveFileData()
        archive_copy.from_json(archive.to_json())
        archive_copy.archive_status = TeraArchiveStatus.STATUS_DELETED.value
        send_archive_event(archive_copy)

        archive.delete_file_archive(flask_app.config['UPLOAD_FOLDER'])

        return gettext('Archive deleted'), 200
