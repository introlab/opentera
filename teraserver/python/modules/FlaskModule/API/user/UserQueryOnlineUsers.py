from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from opentera.db.models.TeraUser import TeraUser
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from modules.DatabaseModule.DBManager import DBManager

get_parser = api.parser()


class UserQueryOnlineUsers(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get online users informations.',
             responses={200: 'Success'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        """
        Get online users
        """
        # args = get_parser.parse_args()
        user_access = DBManager.userAccess(current_user)

        try:
            accessible_users = user_access.get_accessible_users_uuids()

            if not self.test:
                rpc = RedisRPCClient(self.flaskModule.config.redis_config)
                status_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'status_users')
            else:
                status_users = {accessible_users[0]: {'online': True, 'busy': False}}

            users_uuids = [user_uuid for user_uuid in status_users]
            # Filter users that are available to the query
            filtered_user_uuids = list(set(users_uuids).intersection(accessible_users))

            # Query user information
            users = TeraUser.query.filter(TeraUser.user_uuid.in_(filtered_user_uuids))\
                .order_by(TeraUser.user_firstname.asc()).all()
            users_json = [user.to_json(minimal=True) for user in users]
            for user in users_json:
                user['user_online'] = status_users[user['user_uuid']]['online']
                user['user_busy'] = status_users[user['user_uuid']]['busy']

            return users_json

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryOnlineUsers.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Internal server error when making RPC call.'), 500
