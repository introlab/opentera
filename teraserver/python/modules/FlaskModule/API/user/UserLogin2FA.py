from flask_restx import inputs
from flask_babel import gettext
import pyotp
from modules.LoginModule.LoginModule import LoginModule, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.FlaskModule.API.user.UserLoginBase import UserLoginBase
from modules.FlaskModule.API.user.UserLoginBase import OutdatedClientVersionError, \
     UserAlreadyLoggedInError, TooMany2FALoginAttemptsError, InvalidAuthCodeError
import opentera.messages.python as messages
from opentera.redis.RedisVars import RedisVars


# Get parser
get_parser = api.parser()
get_parser.add_argument('otp_code', type=str, required=True, help='2FA otp code')
get_parser.add_argument('with_websocket', type=inputs.boolean,
                        help='If set, requires that a websocket url is returned.'
                             'If not possible to do so, return a 403 error.',
                        default=False)

# Post parser
post_parser = api.parser()
post_parser.add_argument('otp_code', type=str, required=True, help='2FA otp code')
post_parser.add_argument('with_websocket', type=inputs.boolean,
                         help='If set, requires that a websocket url is returned.'
                              'If not possible to do so, return a 403 error.',
                         default=False)


class UserLogin2FA(UserLoginBase):
    """
    UserLogin2FA endpoint resource.
    """

    def __init__(self, _api, *args, **kwargs):
        UserLoginBase.__init__(self, _api, *args, **kwargs)

    # TODO Move this to UserLoginBase ?
    def _common_2fa_login_response(self, parser):
        try:
            # Validate args
            args = parser.parse_args(strict=True)
            response = {}

            self._verify_auth_code()

            # Current user is logged in with HTTPAuth, or session
            # Let's verify if 2FA is enabled and if OTP is valid
            if not current_user.user_2fa_enabled:
                self._user_logout()
                message = gettext('User does not have 2FA enabled')
                self._send_login_failure_message(messages.LoginEvent.LOGIN_STATUS_UNKNOWN, message)
                return message, 403
            if not current_user.user_2fa_otp_enabled or not current_user.user_2fa_otp_secret:
                self._user_logout()
                message = gettext('User does not have 2FA OTP enabled or secret set')
                self._send_login_failure_message(messages.LoginEvent.LOGIN_STATUS_UNKNOWN, message)
                return message, 403

            # Verify OTP
            attempts_key_2fa = RedisVars.RedisVar_User2FALoginAttemptKey + current_user.user_uuid
            totp = pyotp.TOTP(current_user.user_2fa_otp_secret)

            # Increment attempts
            attempts = self.module.redisGet(attempts_key_2fa)
            if attempts:
                attempts = int(attempts) + 1
            else:
                attempts = 1

            # Store attempts in the last 15 minutes
            self.module.redisSet(attempts_key_2fa, attempts, ex=900)

            if not totp.verify(args['otp_code'], valid_window=1):
                self._verify_2fa_login_attempts(current_user.user_uuid)
                message = gettext('Invalid OTP code')
                self._send_login_failure_message(messages.LoginEvent.LOGIN_STATUS_UNKNOWN, message)
                return message, 401

            # Clear attempts
            self.module.redisDelete(attempts_key_2fa)

            # OTP validation completed, proceed with standard login
            version_info = self._verify_client_version()
            if version_info:
                response.update(version_info)

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
        except InvalidAuthCodeError as e:
            self._user_logout()
            return str(e), 403
        except Exception as e:
            # Something went wrong, logout user
            self._user_logout()
            raise e
        else:
            # Everything went well, return response
            response = self._generate_login_success_response(args['with_websocket'], response)
            self._send_login_success_message()
            return response

    @api.doc(description='Login to the server using Session Authentication and 2FA')
    @api.expect(get_parser, validate=True)
    @LoginModule.user_session_required
    def get(self):
        """
        Login to the server using Session Authentication and 2FA
        """
        return self._common_2fa_login_response(get_parser)

    @api.doc(description='Login to the server using Session Authentication and 2FA')
    @api.expect(post_parser, validate=True)
    @LoginModule.user_session_required
    def post(self):
        """
        Login to the server using Session Authentication and 2FA
        """
        return self._common_2fa_login_response(post_parser)
