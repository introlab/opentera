from flask import session, request
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_http_auth, LoginModule, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from opentera.utils.UserAgentParser import UserAgentParser

import opentera.messages.python as messages
from opentera.redis.RedisVars import RedisVars
from opentera.db.models.TeraUser import TeraUser

# model = api.model('Login', {
#     'websocket_url': fields.String,
#     'user_uuid': fields.String,
#     'user_token': fields.String
# })
# Parser definition(s)

get_parser = api.parser()
get_parser.add_argument('with_websocket', type=inputs.boolean, help='If set, requires that a websocket url is returned.'
                                                                    'If not possible to do so, return a 403 error.')


class UserLogin(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Login to the server using HTTP Basic Authentification (HTTPAuth)')
    @api.expect(get_parser)
    @user_http_auth.login_required
    def get(self):
        parser = get_parser
        args = parser.parse_args()

        # Redis key is handled in LoginModule
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        websocket_url = None

        # Get user token key from redis
        token_key = self.module.redisGet(RedisVars.RedisVar_UserTokenAPIKey)

        # Get login informations for log
        login_infos = UserAgentParser.parse_request_for_login_infos(request)

        # Verify if user already logged in
        online_users = []
        if not self.test:
            rpc = RedisRPCClient(self.module.config.redis_config)
            online_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_users')

        if current_user.user_uuid not in online_users:
            websocket_url = "wss://" + servername + ":" + str(port) + "/wss/user?id=" + session['_id']
            print('Login - setting key with expiration in 60s', session['_id'], session['_user_id'])
            self.module.redisSet(session['_id'], session['_user_id'], ex=60)
        elif args['with_websocket']:
            # User is online and a websocket is required
            self.module.logger.send_login_event(sender=self.module.module_name,
                                                level=messages.LogEvent.LOGLEVEL_ERROR,
                                                login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                                login_status=
                                                messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_ALREADY_LOGGED_IN,
                                                client_name=login_infos['client_name'],
                                                client_version=login_infos['client_version'],
                                                client_ip=login_infos['client_ip'],
                                                os_name=login_infos['os_name'],
                                                os_version=login_infos['os_version'],
                                                user_uuid=current_user.user_uuid,
                                                server_endpoint=login_infos['server_endpoint'])

            return gettext('User already logged in.'), 403

        current_user.update_last_online()
        user_token = current_user.get_token(token_key)

        # Return reply as json object
        reply = {"user_uuid": session['_user_id'],
                 "user_token": user_token}
        if websocket_url:
            reply["websocket_url"] = websocket_url

        # Verify client version (optional for now)
        # And add info to reply
        if 'X-Client-Name' in request.headers and 'X-Client-Version' in request.headers:
            try:
                # Extract information
                client_name = request.headers['X-Client-Name']
                client_version = request.headers['X-Client-Version']

                client_version_parts = client_version.split('.')

                # Load known version from database.
                from opentera.utils.TeraVersions import TeraVersions
                versions = TeraVersions()
                versions.load_from_db()

                # Verify if we have client information in DB
                client_info = versions.get_client_version_with_name(client_name)
                if client_info:
                    # We have something stored for this client, let's verify version numbers
                    # For now, we still allow login even when version mismatch
                    # Reply full version information
                    reply['version_latest'] = client_info.to_dict()
                    if client_info.version != client_version:
                        reply['version_error'] = gettext('Client version mismatch')
                        # If major version mismatch, kill client, first part of the version
                        stored_client_version_parts = client_info.version.split('.')
                        if len(stored_client_version_parts) and len(client_version_parts):
                            if stored_client_version_parts[0] != client_version_parts[0]:
                                # return 426 = upgrade required
                                self.module.logger.send_login_event(sender=self.module.module_name,
                                                                    level=messages.LogEvent.LOGLEVEL_ERROR,
                                                                    login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                                                    login_status=
                                                                    messages.LoginEvent.LOGIN_STATUS_UNKNOWN,
                                                                    client_name=login_infos['client_name'],
                                                                    client_version=login_infos['client_version'],
                                                                    client_ip=login_infos['client_ip'],
                                                                    os_name=login_infos['os_name'],
                                                                    os_version=login_infos['os_version'],
                                                                    user_uuid=current_user.user_uuid,
                                                                    server_endpoint=login_infos['server_endpoint'],
                                                                    message=gettext('Client version mismatch'))

                                return gettext('Client major version too old, not accepting login'), 426
                else:
                    return gettext('Invalid client name :') + client_name, 403
            except BaseException as e:
                self.module.logger.log_error(self.module.module_name,
                                             UserLogin.__name__,
                                             'get', 500, 'Invalid client version handler', str(e))
                return gettext('Invalid client version handler') + str(e), 500

        self.module.logger.send_login_event(sender=self.module.module_name,
                                            level=messages.LogEvent.LOGLEVEL_INFO,
                                            login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                            login_status=messages.LoginEvent.LOGIN_STATUS_SUCCESS,
                                            client_name=login_infos['client_name'],
                                            client_version=login_infos['client_version'],
                                            client_ip=login_infos['client_ip'],
                                            os_name=login_infos['os_name'],
                                            os_version=login_infos['os_version'],
                                            user_uuid=current_user.user_uuid,
                                            server_endpoint=login_infos['server_endpoint'])

        return reply
