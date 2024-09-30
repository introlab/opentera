from flask_restx import inputs
from flask_babel import gettext
import pyotp
import pyqrcode
from modules.LoginModule.LoginModule import LoginModule, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.FlaskModule.API.user.UserLoginBase import UserLoginBase
from modules.FlaskModule.API.user.UserLoginBase import OutdatedClientVersionError, \
     UserAlreadyLoggedInError, TooMany2FALoginAttemptsError
from opentera.db.models.TeraUser import TeraUser


# Get parser
get_parser = api.parser()

# Post parser
post_parser = api.parser()
post_parser.add_argument('otp_secret', type=str, required=True, help='OTP Secret for the user.')
post_parser.add_argument('with_email_enabled', type=inputs.boolean,
                        help='Enable email notifications for 2FA', default=False)


class UserLoginSetup2FA(UserLoginBase):
    """
    UserLogin2FA endpoint resource.
    """

    def __init__(self, _api, *args, **kwargs):
        UserLoginBase.__init__(self, _api, *args, **kwargs)

    @api.doc(description='Generate a new 2FA secret and QR Code for the user')
    @api.expect(get_parser, validate=True)
    @LoginModule.user_session_required
    def get(self):
        """
        Generate a new 2FA secret for the user. Will be enabled on post.
        """
        try:
            # Validate args (should not have any)
            get_parser.parse_args(strict=True)
            response = {}

            # Current user is logged in with HTTPAuth, or session
            # Let's verify if 2FA is enabled and if OTP is valid
            if not current_user.user_2fa_enabled:
                self._user_logout()
                return gettext('User does not have 2FA enabled'), 403

            if current_user.user_2fa_otp_secret:
                self._user_logout()
                return gettext('User already has 2FA OTP secret set'), 403

            # Verify if user has tried too many times to login with 2FA
            # This should not happen here, but just in case
            self._verify_2fa_login_attempts(current_user.user_uuid)

            # Generate new secret
            secret = pyotp.random_base32()

            # Generate OTP URI for QR Code
            totp = pyotp.TOTP(secret)

            # Get the server name in the config
            server_name = self.module.config.server_config['name']
            otp_uri = totp.provisioning_uri(current_user.user_username,
                                            issuer_name=f'OpenTera-{server_name}')

            # Generate QR Code with otp_uri
            qr_code = pyqrcode.create(otp_uri)

            # Generate image as base64
            qr_code_base64 = qr_code.png_as_base64_str(scale=5)

            response['qr_code'] = qr_code_base64
            response['otp_secret'] = secret

        except OutdatedClientVersionError as e:
            self._user_logout()
            return {
                'version_latest': e.version_latest,
                'current_version': e.current_version,
                'version_error': e.version_error,
                'message': gettext('Client major version too old, not accepting login')}, 426
#        except InvalidClientVersionError as e:
#            # Invalid client version, will not be handled for now
#            pass
        except UserAlreadyLoggedInError as e:
            self._user_logout()
            return str(e), 403
        except TooMany2FALoginAttemptsError as e:
            self._user_logout()
            return str(e), 403
        except Exception as e:
            # Something went wrong, logout user
            self._user_logout()
            raise e
        else:
            # Everything went well, return response
            return response, 200


    @api.doc(description='Enable 2FA for the user')
    @api.expect(post_parser, validate=True)
    @LoginModule.user_session_required
    def post(self):
        """
        Enable 2FA for the user. Will use the OTP secret generated in the GET method.
        """
        try:
            args = post_parser.parse_args(strict=True)
            response = {}

            # Current user is logged in with HTTPAuth, or session
            # Let's verify if 2FA is enabled and if OTP is valid
            if not current_user.user_2fa_enabled:
                self._user_logout()
                return gettext('User does not have 2FA enabled'), 403

            if current_user.user_2fa_otp_secret:
                self._user_logout()
                return gettext('User already has 2FA OTP secret set'), 403

            # Verify if user has tried too many times to login with 2FA
            # This should not happen here, but just in case
            self._verify_2fa_login_attempts(current_user.user_uuid)

            data = {'user_2fa_enabled': True,
                    'user_2fa_otp_enabled': True,
                    'user_2fa_otp_secret': args['otp_secret'],
                    'user_2fa_email_enabled': args['with_email_enabled']}

            # Save user to db
            TeraUser.update(current_user.id_user, data)

            # Redirect to 2FA validation page
            response['message'] = gettext('2FA enabled for this user.')
            response['redirect_url'] = self._generate_2fa_verification_url()

        except OutdatedClientVersionError as e:
            self._user_logout()
            return {
                'version_latest': e.version_latest,
                'current_version': e.current_version,
                'version_error': e.version_error,
                'message': gettext('Client major version too old, not accepting login')}, 426
#        except InvalidClientVersionError as e:
#            # Invalid client version, will not be handled for now
#            pass
        except UserAlreadyLoggedInError as e:
            self._user_logout()
            return str(e), 403
        except TooMany2FALoginAttemptsError as e:
            self._user_logout()
            return str(e), 403
        except Exception as e:
            # Something went wrong, logout user
            self._user_logout()
            raise e
        else:
            # Everything went well, return response
            return response, 200
