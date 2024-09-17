from flask.views import MethodView
from flask import render_template, request, redirect, url_for, session, jsonify
from opentera.utils.TeraVersions import TeraVersions
from modules.LoginModule.LoginModule import current_user, LoginModule
from opentera.db.models.TeraUser import TeraUser
from flask_babel import gettext
from opentera.utils.UserAgentParser import UserAgentParser

import opentera.messages.python as messages
from opentera.redis.RedisVars import RedisVars
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames


class LoginValidate2FAView(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @LoginModule.user_session_required
    def get(self):
        """
        GET method for the login enable 2FA page. This page is displayed when a user logs in and has 2FA disabled.
        User must be authenticated to access this page. User will need to set 2FA to continue.
        """

        # Verify if user is authenticated, should be stored in session
        # Return to login page
        if not current_user:
            return redirect(url_for('login'))

        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']

        if 'X_EXTERNALSERVER' in request.headers:
            hostname = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        versions = TeraVersions()
        versions.load_from_db()

        return render_template('login_validate_2fa.html', hostname=hostname, port=port,
                               server_version=versions.version_string,
                               openteraplus_version=versions.get_client_version_with_name('OpenTeraPlus'))

    @LoginModule.user_session_required
    def post(self):
        # Verify the form
        if '2fa_code' not in request.form:
            return gettext('Missing 2FA code'), 400

        # Get the user's 2FA code from the form
        code = request.form['2fa_code']

        # TODO Should use LoginModule instead of TeraUser directly ?
        # Check the user's 2FA code
        if not current_user.verify_2fa(code):
            return gettext('Invalid 2FA code'), 401

        # TODO This is duplication from the API login endpoint, how to avoid this ?
        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']

        if 'X_EXTERNALSERVER' in request.headers:
            hostname = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        # Generate user token
        # Get user token key from redis
        token_key = self.flaskModule.redisGet(RedisVars.RedisVar_UserTokenAPIKey)

        # Get login information for log
        login_info = UserAgentParser.parse_request_for_login_infos(request)

        # Verify if user already logged in
        online_users = []
        websocket_url = None

        if not self.test:
            rpc = RedisRPCClient(self.flaskModule.config.redis_config)
            online_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_users')

        if current_user.user_uuid not in online_users:
            websocket_url = "wss://" + hostname + ":" + str(port) + "/wss/user?id=" + session['_id']
            self.flaskModule.redisSet(session['_id'], session['_user_id'], ex=60)
        else:
            # User is online and a websocket is required
            self.flaskModule.logger.send_login_event(sender=self.flaskModule.module_name,
                                                     level=messages.LogEvent.LOGLEVEL_ERROR,
                                                     login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                                     login_status=
                                                     messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_ALREADY_LOGGED_IN,
                                                     client_name=login_info['client_name'],
                                                     client_version=login_info['client_version'],
                                                     client_ip=login_info['client_ip'],
                                                     os_name=login_info['os_name'],
                                                     os_version=login_info['os_version'],
                                                     user_uuid=current_user.user_uuid,
                                                     server_endpoint=login_info['server_endpoint'])

            return gettext('User already logged in.'), 403

        current_user.update_last_online()
        user_token = current_user.get_token(token_key)

        reply = {"user_uuid": session['_user_id'],
                 "user_token": user_token,
                 "websocket_url": websocket_url}

        return jsonify(reply)



