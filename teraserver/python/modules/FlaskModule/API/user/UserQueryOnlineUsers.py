from flask import session
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
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

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get online users informations.',
             responses={200: 'Success'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        parser = get_parser
        args = parser.parse_args()
        user_access = DBManager.userAccess(current_user)

        try:
            accessible_users = user_access.get_accessible_users_uuids()
            rpc = RedisRPCClient(self.flaskModule.config.redis_config)
            status_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'status_users')

            users_uuids = [user_uuid for user_uuid in status_users]
            # Filter users that are available to the query
            filtered_user_uuids = list(set(users_uuids).intersection(accessible_users))

            # Query user information
            users = TeraUser.query.filter(TeraUser.user_uuid.in_(filtered_user_uuids)).all()
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

    # def post(self):
    #     return '', 501
    #
    # def delete(self):
    #     return '', 501

