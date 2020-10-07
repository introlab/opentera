from flask import session
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.redis.RedisRPCClient import RedisRPCClient
from modules.BaseModule import ModuleNames
from modules.DatabaseModule.DBManager import DBManager

get_parser = api.parser()
get_parser.add_argument('with_busy', type=inputs.boolean, help='Also return users that are busy.')


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
            online_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_users')

            # Filter users that are available to the querier
            online_user_uuids = list(set(online_users).intersection(accessible_users))

            # Query user informations
            users = TeraUser.query.filter(TeraUser.user_uuid.in_(online_user_uuids)).all()
            users_json = [user.to_json(minimal=True) for user in users]
            for user in users_json:
                user['user_online'] = True

            # Also query busy users?
            if args['with_busy']:
                busy_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'busy_users')

                # Filter users that are available to the querier
                busy_user_uuids = list(set(busy_users).intersection(accessible_users))

                # Query user informations
                busy_users = TeraUser.query.filter(TeraUser.user_uuid.in_(busy_user_uuids)).all()
                busy_users_json = [user.to_json(minimal=True) for user in busy_users]
                for user in busy_users_json:
                    user['user_busy'] = True
                users_json.extend(busy_users_json)

            return users_json

        except InvalidRequestError:
            return gettext('Internal server error when making RPC call.'), 500

    # def post(self):
    #     return '', 501
    #
    # def delete(self):
    #     return '', 501

