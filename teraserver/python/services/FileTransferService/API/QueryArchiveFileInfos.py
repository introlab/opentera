from flask import request
from flask_babel import gettext
from flask_restx import Resource
from services.FileTransferService.FlaskModule import file_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_service_client, current_user_client
from opentera.services.ServiceAccessManager import current_login_type, LoginType
from opentera.services.ServiceAccessManager import current_device_client, current_participant_client
from services.FileTransferService.libfiletransferservice.db.models.ArchiveFileData import ArchiveFileData
from werkzeug.utils import secure_filename
from services.FileTransferService.API.send_archive_event import send_archive_event
import datetime

# Parser definition(s)
get_parser = api.parser()

get_parser.add_argument('archive_uuid', type=str, required=True, help='UUID of the archive to get info')

post_schema = api.schema_model('archive',
                               {'properties':
                                   {
                                        'id_archive_file_data':
                                        {
                                           'type': 'integer',
                                           'location': 'json'
                                        },
                                        'archive_original_filename':
                                        {
                                           'type': 'string',
                                           'location': 'json'
                                        },
                                        'archive_owner_uuid':
                                        {
                                              'type': 'string',
                                              'location': 'json'
                                        },
                                        'archive_status':
                                        {
                                              'type': 'integer',
                                              'location': 'json'
                                        }
                                   }
                                }
                               )


class QueryArchiveFileInfos(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.expect(get_parser, validate=True)
    @api.doc(description='Query information about stored archive',
             responses={200: 'Success - Return information about archive',
                        400: 'Bad request',
                        403: 'Access denied to the requested archive'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def get(self):
        args = get_parser.parse_args()

        archive = ArchiveFileData.get_archive_by_uuid(uuid_archive=args['archive_uuid'])

        if not archive:
            return gettext('No archive found'), 404

        if current_login_type == LoginType.USER_LOGIN:
            if archive.archive_owner_uuid != current_user_client.user_uuid:
                return gettext('Access denied for that archive'), 403
            return archive.to_json()
        elif current_login_type == LoginType.PARTICIPANT_LOGIN:
            if archive.archive_owner_uuid != current_participant_client.participant_uuid:
                return gettext('Access denied for that archive'), 403
            return archive.to_json()
        elif current_login_type == LoginType.DEVICE_LOGIN:
            if archive.archive_owner_uuid != current_device_client.device_uuid:
                return gettext('Access denied for that archive'), 403
            return archive.to_json()
        elif current_login_type == LoginType.SERVICE_LOGIN:
            return archive.to_json()

        return gettext('Access denied for that archive'), 403

    @api.expect(post_schema, validate=False)
    @api.doc(description='Update information about stored archive',
             responses={200: 'Success - Return information about file archive',
                        400: 'Required parameter is missing',
                        403: 'Access denied to the requested archive'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=True)
    def post(self):
        if 'archive' not in request.json:
            return gettext('Badly formatted request'), 400

        archive_info = request.json['archive']

        if 'id_archive_file_data' not in archive_info:
            return gettext('Badly formatted request'), 400

        if 'archive_original_filename' not in archive_info:
            return gettext('Missing original filename'), 400

        if 'archive_owner_uuid' not in archive_info:
            return gettext('Missing owner UUID'), 400

        if archive_info['id_archive_file_data'] == 0:
            archive = ArchiveFileData()
            try:
                archive.from_json(archive_info)

                # Add Creation datetime
                archive.archive_creation_datetime = datetime.datetime.now(datetime.timezone.utc)

                # Add Expiration datetime in 30 days
                archive.archive_expiration_datetime = archive.archive_creation_datetime + datetime.timedelta(days=30)

                # Make sure file name is secure
                archive.archive_original_filename = secure_filename(archive.archive_original_filename)
                ArchiveFileData.insert(archive)
            except Exception as e:
                return gettext('Error parsing archive information'), 400

            # Send event
            send_archive_event(archive)

            # Send response
            return archive.to_json()

        else:
            # Only allow status update for now
            archive = ArchiveFileData.get_archive_by_id(archive_info['id_archive_file_data'])
            if archive is None:
                return gettext('No archive found'), 404

            if 'archive_status' not in archive_info:
                return gettext('Missing archive status'), 400
            else:
                try:
                    archive.archive_status = archive_info['archive_status']
                    archive.commit()
                except Exception as e:
                    return gettext('Error parsing archive information'), 400

                # Send event
                send_archive_event(archive)

                # Send response
                return archive.to_json()
