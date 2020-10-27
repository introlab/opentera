from flask import jsonify, session, request
from flask_restx import Resource, reqparse, fields
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_http_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.redis.RedisRPCClient import RedisRPCClient
from modules.BaseModule import ModuleNames

# model = api.model('Login', {
#     'websocket_url': fields.String,
#     'user_uuid': fields.String,
#     'user_token': fields.String
# })
# Parser definition(s)

get_parser = api.parser()


class UserLogin(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.parser = reqparse.RequestParser()

    @user_http_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Login to the server using HTTP Basic Authentification (HTTPAuth)')
    def get(self):

        session.permanent = True

        # Redis key is handled in LoginModule
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']
        if 'X_EXTERNALHOST' in request.headers:
            if ':' in request.headers['X_EXTERNALHOST']:
                servername, port = request.headers['X_EXTERNALHOST'].split(':', 1)
            else:
                servername = request.headers['X_EXTERNALHOST']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        # Get user token key from redis
        from modules.RedisVars import RedisVars
        token_key = self.module.redisGet(RedisVars.RedisVar_UserTokenAPIKey)

        # Get token for user
        from libtera.db.models.TeraUser import TeraUser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])

        # Verify if user already logged in
        rpc = RedisRPCClient(self.module.config.redis_config)
        online_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_users')
        if current_user.user_uuid in online_users:
            self.module.logger.log_warning(self.module.module_name,
                                           UserLogin.__name__,
                                           'get', 403,
                                           'User already logged in', current_user.to_json(minimal=True))
            return gettext('User already logged in.'), 403

        current_user.update_last_online()
        user_token = current_user.get_token(token_key)

        print('Login - setting key with expiration in 60s', session['_id'], session['_user_id'])
        self.module.redisSet(session['_id'], session['_user_id'], ex=60)

        # Return reply as json object
        reply = {"websocket_url": "wss://" + servername + ":" + str(port) + "/wss/user?id=" + session['_id'],
                 "user_uuid": session['_user_id'],
                 "user_token": user_token}

        # Verify client version (optional for now)
        # And add info to reply
        if 'X-Client-Name' in request.headers and 'X-Client-Version' in request.headers:
            try:
                # Extract information
                client_name = request.headers['X-Client-Name']
                client_version = request.headers['X-Client-Version']

                client_version_parts = client_version.split('.')

                # Load known version from database.
                from libtera.utils.TeraVersions import TeraVersions
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
                                self.module.logger.log_warning(self.module.module_name,
                                                               UserLogin.__name__,
                                                               'get', 426,
                                                               'Client major version too old, not accepting login',
                                                               stored_client_version_parts[0],
                                                               client_version_parts[0])
                                return gettext('Client major version too old, not accepting login'), 426
                else:
                    return gettext('Invalid client name :') + client_name, 403
            except BaseException as e:
                self.module.logger.log_error(self.module.module_name,
                                             UserLogin.__name__,
                                             'get', 500, 'Invalid client version handler', str(e))
                return gettext('Invalid client version handler') + str(e), 500

        return reply
