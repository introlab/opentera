from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule
from modules.FlaskModule.FlaskModule import service_api_ns as api
from opentera.db.models.TeraProject import TeraProject
from sqlalchemy.exc import InvalidRequestError

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='ID of the project to query')


class ServiceQueryProjects(Resource):

    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return projects information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        parser = get_parser
        args = parser.parse_args()

        projects = []
        # Can only query project with an id
        if not args['id_project']:
            return gettext('Missing project id', 400)

        if args['id_project']:
            projects = [TeraProject.get_project_by_id(args['id_project'])]

        try:
            projects_list = []
            for project in projects:
                project_json = project.to_json(minimal=True)
                projects_list.append(project_json)

            return projects_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryProjects.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500
