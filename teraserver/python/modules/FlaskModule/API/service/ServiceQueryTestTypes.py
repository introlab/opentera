from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraParticipant import TeraParticipant


# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_site', type=int, help='ID of the site to query test types for')
get_parser.add_argument('id_project', type=int, help='ID of the project to query test types for')
get_parser.add_argument('id_participant', type=int, help='ID of the participant to query types for')
get_parser.add_argument('test_type_key', type=str, help='Test type key to query for')
get_parser.add_argument('id_test_type', type=int, help='ID of the test type to query for')


class ServiceQueryTestTypes(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return test types information for the current service',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        args = get_parser.parse_args(strict=True)
        service_access = DBManager.serviceAccess(current_service)

        test_types = []
        if args['id_site']:
            if args['id_site'] in service_access.get_accessibles_sites_ids():
                test_types = [tt.test_type_site_test_type for tt in
                              TeraTestTypeSite.get_tests_types_for_site(args['id_site'])]
        elif args['id_project']:
            if args['id_project'] in service_access.get_accessible_projects_ids():
                test_types = [tt.test_type_project_test_type for tt in
                              TeraTestTypeProject.get_tests_types_for_project(args['id_project'])]
        elif args['id_participant']:
            if args['id_participant'] in service_access.get_accessible_participants_ids():
                part_info = TeraParticipant.get_participant_by_id(args['id_participant'])
                test_types = [tt.test_type_project_test_type for tt in
                              TeraTestTypeProject.get_tests_types_for_project(part_info.id_project)]
        elif args['id_test_type']:
            if args['id_test_type'] in service_access.get_accessible_tests_types_ids():
                test_types = [TeraTestType.get_test_type_by_id(args['id_test_type'])]
        elif args['test_type_key']:
            test_type = TeraTestType.get_test_type_by_key(args['test_type_key'])
            if test_type and test_type.id_test_type in service_access.get_accessible_tests_types_ids():
                test_types = [test_type]
        else:
            test_types = service_access.get_accessible_tests_types()

        return [tt.to_json() for tt in test_types]
