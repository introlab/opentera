from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager

from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSite import TeraSite
from sqlalchemy.exc import InvalidRequestError

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='ID of the project to query')
get_parser.add_argument('id_site', type=int, help='ID of the site to query projects for')


class ServiceQueryProjects(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return projects information.',
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

        projects = []
        # Can only query project with an id
        if not args['id_project'] and not args['id_site']:
            return gettext('Missing parameter'), 400

        if args['id_project']:
            if args['id_project'] not in service_access.get_accessible_projects_ids():
                return gettext('Forbidden'), 403
            projects = [TeraProject.get_project_by_id(args['id_project'])]

        if args['id_site']:
            if args['id_site'] not in service_access.get_accessibles_sites_ids():
                return gettext('Forbidden'), 403
            projects = TeraSite.get_site_by_id(args['id_site']).site_projects

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
