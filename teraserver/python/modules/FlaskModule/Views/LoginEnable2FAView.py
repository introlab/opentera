from flask.views import MethodView
from flask import render_template, request, redirect, url_for, session
from opentera.utils.TeraVersions import TeraVersions
from modules.LoginModule.LoginModule import current_user, LoginModule
import pyotp
import pyqrcode


class LoginEnable2FAView(MethodView):

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

        # Generate a new secret for the user
        current_user.user_2fa_enabled = False
        current_user.user_2fa_enabled = False
        current_user.user_2fa_otp_enabled = True
        current_user.user_2fa_email_enabled = False
        current_user.user_2fa_otp_secret = pyotp.random_base32()
        # TODO Save user to db

        # Generate OTP URI for QR Code
        totp = pyotp.TOTP(current_user.user_2fa_otp_secret)

        # TODO issuer_name should be configurable for each server
        otp_uri = totp.provisioning_uri(current_user.user_email, issuer_name='OpenTera')

        # Generate QR Code with otp_uri
        qr_code = pyqrcode.create(otp_uri)

        # Generate image as base64
        qr_code_base64 = qr_code.png_as_base64_str(scale=5)

        return render_template('login_enable_2fa.html', hostname=hostname, port=port,
                               server_version=versions.version_string,
                               qr_code=qr_code_base64,
                               openteraplus_version=versions.get_client_version_with_name('OpenTeraPlus'))

    @LoginModule.user_session_required
    def post(self):
        pass



