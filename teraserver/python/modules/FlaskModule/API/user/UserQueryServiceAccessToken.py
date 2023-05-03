from flask_restx import Resource, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraService import TeraService
from modules.DatabaseModule.DBManager import DBManager
from opentera.redis.RedisVars import RedisVars
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_service', type=int, help='ID service to generate access token')
get_parser.add_argument('with_sites', type=inputs.boolean, help='Include site roles in token', default=False)
get_parser.add_argument('with_projects', type=inputs.boolean, help='Include projects roles in token', default=False)


class UserQueryServiceAccessToken(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get access token for a specific service.',
             responses={200: 'Success - returns access token',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting association'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

        if not args['id_service']:
            return gettext('Missing id_service'), 400

        if args['id_service'] not in user_access.get_accessible_services_ids():
            return gettext('No access to specified service'), 403

        # 'user_access': {'services': {'service_key': {'projects':
        #                                                 [('id_project2', 'admin'), ('id_project3', 'user')],
        #                                             'sites':
        #                                                 [('id_site1', 'admin')],
        #                                             'global': ['manager', 'admin']
        #                                             }
        #                             }
        #                }

        user_access = {'services': {}}
        service_info = TeraService.get_service_by_id(args['id_service'])
        service_global_roles = current_user.get_service_roles(args['id_service'])
        user_access['services'][service_info.service_key] = {'global': service_global_roles}

        if args['with_sites']:
            site_roles = current_user.get_sites_roles(id_service=args['id_service'])
            user_access['services'][service_info.service_key]['sites'] = {
                [(sr['site'].id_site, sr['site_role']) for sr in site_roles]
            }

        if args['with_projects']:
            project_roles = current_user.get_projects_roles(id_service=args['id_service'])
            user_access['services'][service_info.service_key]['projects'] = {
                [(pr['project'].id_project, pr['project_role']) for pr in project_roles]
            }

        # Get user token key from redis
        token_key = self.module.redisGet(RedisVars.RedisVar_UserTokenAPIKey)

        # Create and return token
        token = current_user.get_service_access_token(token_key=token_key, content=user_access)

        return token
