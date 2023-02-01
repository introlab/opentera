from flask import session, request
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_token_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.LoginModule.LoginModule import LoginModule
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from opentera.redis.RedisVars import RedisVars

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('with_websocket', type=inputs.boolean, help='If set, requires that a websocket url is returned.'
                                                                    'If not possible to do so, return a 403 error.')


class UserRefreshToken(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Refresh token, old token needs to be passed in request headers.',
             responses={200: 'Success',
                        500: 'Server error'})
    @api.expect(get_parser)
    @user_token_auth.login_required
    def get(self):
        # If we have made it this far, token passed in headers was valid.
        # Get user token key from redis
        token_key = self.module.redisGet(RedisVars.RedisVar_UserTokenAPIKey)

        # Get token for user
        args = get_parser.parse_args()

        websocket_url = None
        if args['with_websocket']:
            session.permanent = True

            # Redis key is handled in LoginModule
            servername = self.module.config.server_config['hostname']
            port = self.module.config.server_config['port']
            if 'X_EXTERNALSERVER' in request.headers:
                servername = request.headers['X_EXTERNALSERVER']

            if 'X_EXTERNALPORT' in request.headers:
                port = request.headers['X_EXTERNALPORT']

            # Verify if user already logged in with a websocket
            rpc = RedisRPCClient(self.module.config.redis_config)
            online_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_users')
            if current_user.user_uuid not in online_users:
                # User is online and a websocket is required
                # self.module.logger.log_warning(self.module.module_name,
                #                                UserRefreshToken.__name__,
                #                                'get', 403,
                #                                'User already logged in', current_user.to_json(minimal=True))
                # return gettext('User already logged in.'), 403
                # User doesn't currently have a websocket connection
                websocket_url = "wss://" + servername + ":" + str(port) + "/wss/user?id=" + session['_id']
                print('Login - setting key with expiration in 60s', session['_id'], session['_user_id'])
                self.module.redisSet(session['_id'], session['_user_id'], ex=60)

        # Put old token in disabled tokens
        scheme, old_token = request.headers['Authorization'].split(None, 1)
        if len(old_token) > 0:
            LoginModule.user_push_disabled_token(old_token)

        # Regenerate token, 30 minutes expiration
        user_token = current_user.get_token(token_key, expiration=60 * 30)

        # Return reply as json object
        reply = {"refresh_token": user_token}
        if websocket_url:
            reply['websocket_url'] = websocket_url;

        return reply
