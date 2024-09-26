from flask.views import MethodView
from flask import render_template, request, redirect, url_for, session
from opentera.utils.TeraVersions import TeraVersions
from modules.LoginModule.LoginModule import current_user, LoginModule
from opentera.db.models.TeraUser import TeraUser
import pyotp
import pyqrcode
from flask_babel import gettext


class LoginSetup2FAView(MethodView):

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

        return render_template('login_setup_2fa.html', hostname=hostname, port=port,
                               server_version=versions.version_string)

    @LoginModule.user_session_required
    def post(self):
        # Verify if user is authenticated, should be stored in session
        if not current_user:
            return redirect(url_for('login'))

        if 'enable_2fa' in request.form and request.form['enable_2fa'] == 'on' and 'otp_secret' in request.form:
            # Enable 2FA
            current_user.user_2fa_enabled = True
            current_user.user_2fa_otp_enabled = True
            current_user.user_2fa_email_enabled = False
            # Save user to db
            # TODO enable email 2FA
            TeraUser.update(current_user.id_user, {'user_2fa_enabled': True,
                                                   'user_2fa_otp_enabled': True,
                                                   'user_2fa_otp_secret': request.form['otp_secret'],
                                                   'user_2fa_email_enabled': False})

            # Redirect to 2FA validation page
            return redirect(url_for('login_validate_2fa'))

        # Redirect to login page
        return redirect(url_for('login'))
