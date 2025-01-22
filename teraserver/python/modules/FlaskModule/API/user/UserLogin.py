from flask_restx import inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import current_user, user_http_login_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.FlaskModule.API.user.UserLoginBase import UserLoginBase
from modules.FlaskModule.API.user.UserLoginBase import OutdatedClientVersionError, \
     UserAlreadyLoggedInError, TooMany2FALoginAttemptsError, InvalidAuthCodeError



get_parser = api.parser()
get_parser.add_argument('with_websocket', type=inputs.boolean, default=False,
                            help='If set, requires that a websocket url is returned.'
                            'If not possible to do so, return a 403 error.')

class UserLogin(UserLoginBase):
    """
    UserLogin Resource.
    """
    def __init__(self, _api, *args, **kwargs):
        UserLoginBase.__init__(self, _api, *args, **kwargs)


    @api.doc(description='Login to the server using HTTP Basic Authentication (HTTPAuth)',
             security='basicAuth')
    @api.expect(get_parser)
    @user_http_login_auth.login_required
    def get(self):
        """
        Login to the server using HTTP Basic Authentication
        """
        try:
            # Validate args
            args = get_parser.parse_args(strict=True)
            response = {}

            version_info = self._verify_client_version()
            if version_info:
                response.update(version_info)

            # Verify if auth code is valid
            self._verify_auth_code()

            # User needs to change password?
            if current_user.user_force_password_change:
                response['message'] = gettext('Password change required for this user.')
                response['reason'] = 'password_change'
                response['redirect_url'] = self._generate_password_change_url()
            else:
                # 2FA enabled? Client will need to proceed to 2FA login step first
                if current_user.user_2fa_enabled:
                    # If user had too many 2FA login failures, stop login process
                    self._verify_2fa_login_attempts(current_user.user_uuid)

                    if current_user.user_2fa_otp_enabled and current_user.user_2fa_otp_secret:
                        response['message'] = gettext('2FA required for this user.')
                        response['reason'] = '2fa'
                        response['redirect_url'] = self._generate_2fa_verification_url()
                    else:
                        response['message'] = gettext('2FA enabled but OTP not set for this user.'
                                                      'Please setup 2FA.')
                        response['reason'] = '2fa_setup'
                        response['redirect_url'] = self._generate_2fa_setup_url()
                else:
                    response = self._generate_login_success_response(args['with_websocket'], response)
                    # Only with non-2FA users, otherwise, we wait for 2FA to be completed
                    self._send_login_success_message()

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
        except InvalidAuthCodeError as e:
            self._user_logout()
            return str(e), 403
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
            return response
