from flask_restx import Resource
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraParticipant import TeraParticipant

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_site', type=int, help='ID of the site to query session types for')
get_parser.add_argument('id_project', type=int, help='ID of the project to query session types for')
get_parser.add_argument('id_participant', type=int, help='ID of the participant to query types for')
get_parser.add_argument('id_session_type', type=int, help='ID of the session type to query')


class ServiceQuerySessionTypes(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return session types information for the current service',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        args = get_parser.parse_args()
        service_access = DBManager.serviceAccess(current_service)

        session_types = []
        if args['id_site']:
            if args['id_site'] in service_access.get_accessibles_sites_ids():
                session_types = [st.session_type_site_session_type for st in
                                 TeraSessionTypeSite.get_sessions_types_for_site(args['id_site'])]
        elif args['id_project']:
            if args['id_project'] in service_access.get_accessible_projects_ids():
                session_types = [st.session_type_project_session_type for st in
                                 TeraSessionTypeProject.get_sessions_types_for_project(args['id_project'])]
        elif args['id_participant']:
            if args['id_participant'] in service_access.get_accessible_participants_ids():
                part_info = TeraParticipant.get_participant_by_id(args['id_participant'])
                session_types = [st.session_type_project_session_type for st in
                                 TeraSessionTypeProject.get_sessions_types_for_project(part_info.id_project)]
        elif args['id_session_type']:
            if args['id_session_type'] in service_access.get_accessible_sessions_types_ids():
                session_types = [TeraSessionType.get_session_type_by_id(args['id_session_type'])]
        else:
            session_types = service_access.get_accessible_sessions_types()

        return [st.to_json() for st in session_types]
