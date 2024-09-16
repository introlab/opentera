from flask.views import MethodView
from flask import render_template, request, redirect, url_for, session
from opentera.utils.TeraVersions import TeraVersions
from modules.LoginModule.LoginModule import current_user, LoginModule


class Login2FAView(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

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

        return render_template('login_2fa.html', hostname=hostname, port=port,
                               server_version=versions.version_string,
                               openteraplus_version=versions.get_client_version_with_name('OpenTeraPlus'))

    def post(self):
        pass



