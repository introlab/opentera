from flask_restx import Resource
from services.BureauActif import Globals
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_login_type, current_device_client, \
    current_participant_client, current_user_client, LoginType
from services.BureauActif.FlaskModule import default_api_ns as api

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='ID of the project for which to fetch the role')
get_parser.add_argument('id_site', type=int, help='ID of the site for which to fetch the role')


class QueryPermissions(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.expect(get_parser)
    @api.doc(description='Gets current login type: device, participant or user and associated informations',
             responses={200: 'Success'})
    @ServiceAccessManager.token_required
    def get(self):
        parser = get_parser
        args = parser.parse_args()
        permissions = {
            'site_admin': False,
            'project_admin': False,
        }

        # Get role of user for either site or project
        params = {}
        if args['id_project'] or args['id_site']:
            if args['id_project']:
                params = {'id_project': args['id_project'], 'uuid_user': current_user_client.user_uuid}
            if args['id_site']:
                params = {'id_site': args['id_site'], 'uuid_user': current_user_client.user_uuid}

            endpoint = '/api/service/users/access'
            response = Globals.service.get_from_opentera(endpoint, params)

            if response.status_code == 200:
                role = response.json()
                if args['id_project']:
                    project_admin = True if role['project_role'] == 'admin' else False
                    permissions.update({'project_admin': project_admin})
                if args['id_site']:
                    site_admin = True if role['site_role'] == 'admin' else False
                    permissions.update({'site_admin': site_admin})

        return permissions
