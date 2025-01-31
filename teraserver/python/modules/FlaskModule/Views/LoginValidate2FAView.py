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

        # Not specified or with no value will default to true
        with_websocket = request.args.get('with_websocket', '').lower() in ['true', '1', 'yes', 'on', '']

        return render_template('login_validate_2fa.html', hostname=hostname, port=port,
                               server_version=versions.version_string,
                               with_websocket=with_websocket)
