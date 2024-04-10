from flask import request
from flask_babel import gettext
from flask_restx import Resource
from services.FileTransferService.FlaskModule import file_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager
from services.FileTransferService.libfiletransferservice.db.models.ArchiveFileData import ArchiveFileData
import services.FileTransferService.Globals as Globals

# Parser definition(s)
get_parser = api.parser()

get_parser.add_argument('archive_uuid', type=str, required=True, help='UUID of the archive to get info')

post_schema = api.schema_model('archive',
                               {'properties':
                                   {
                                       'archive_uuid':
                                           {
                                               'type': 'string',
                                               'location': 'json'
                                           }
                                   }
                                })


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

        # TODO verify archive access
        archive = ArchiveFileData.get_archive_by_uuid(uuid_archive=args['archive_uuid'])

        if not archive:
            return gettext('No archive found'), 404

        return archive.to_json()

    @api.expect(post_schema)
    @api.doc(description='Update information about stored archive',
             responses={200: 'Success - Return information about file archive',
                        400: 'Required parameter is missing',
                        403: 'Access denied to the requested archive'})
    @ServiceAccessManager.service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=True)
    def post(self):
        if 'archive' not in request.json:
            return gettext('Badly formatted request'), 400

        archive_info = request.json['archive']
        # if 'id_archive_file_data' not in archive_info:
        #     return gettext('Badly formatted request'), 400
        #
        # if archive_info['id_archive_file_data'] == 0:
        #     # Create new archive
        #     archive = ArchiveFileData()
        #     ArchiveFileData.insert(archive)

        return gettext('Not implemented yet'), 501


