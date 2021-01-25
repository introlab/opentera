from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='ID of the project to query')
get_parser.add_argument('id_site', type=int, help='ID of the site to query')
get_parser.add_argument('uuid_user', type=str, help='UUID of the user')


class ServiceQuerySiteProjectAccessRoles(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return sessions information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        parser = get_parser
        args = parser.parse_args()
        service_access = DBManager.serviceAccess(current_service)

        project_admin_info = {
            'project_role': 'user',
        }
        site_admin_info = {
            'site_role': 'user',
        }

        # Can only query permissions with an id
        if not args['id_project'] and not args['id_site']:
            return gettext('Missing arguments', 400)

        if args['id_project']:
            project_admin_info['project_role'] = service_access.get_project_role(args['id_project'], args['uuid_user'])
            return project_admin_info

        if args['id_site']:
            site_admin_info['site_role'] = service_access.get_site_role(args['id_site'], args['uuid_user'])
            return site_admin_info
