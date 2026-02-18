from flask.views import MethodView
from flask import render_template, request, session
from opentera.utils.TeraVersions import TeraVersions
from modules.LoginModule.LoginModule import current_user, LoginModule

class LoginChangePasswordView(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @LoginModule.user_session_required
    def get(self):
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

        return render_template('login_change_password.html', hostname=hostname, port=port,
                               server_version=versions.version_string, username=current_user.user_username,
                               with_websocket=with_websocket, theme_file=session['theme'],)
