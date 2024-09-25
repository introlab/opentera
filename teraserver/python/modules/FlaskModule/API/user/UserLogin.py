from flask import session, request
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from flask_login import logout_user
from modules.LoginModule.LoginModule import user_http_auth, LoginModule, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from opentera.utils.UserAgentParser import UserAgentParser

import opentera.messages.python as messages
from opentera.redis.RedisVars import RedisVars

from modules.FlaskModule.API.user.UserLoginBase import UserLoginBase
from modules.FlaskModule.API.user.UserLoginBase import OutdatedClientVersionError, InvalidClientVersionError, \
     UserAlreadyLoggedInError


get_parser = api.parser()
get_parser.add_argument('with_websocket', type=inputs.boolean, default=False,
                            help='If set, requires that a websocket url is returned. If not possible to do so, return a 403 error.')

post_parser = api.parser()
post_parser.add_argument('with_websocket', type=inputs.boolean, default=False,
                            help='If set, requires that a websocket url is returned. If not possible to do so, return a 403 error.')

class UserLogin(UserLoginBase):
    """
    UserLogin Resource.
    """

    def __init__(self, _api, *args, **kwargs):
        UserLoginBase.__init__(self, _api, *args, **kwargs)

    def _common_login_response(self, parser):
        try:
            # Validate args
            args = parser.parse_args(strict=True)
            response = {}

            version_info = self._verify_client_version()
            if version_info:
                response.update(version_info)

            # 2FA enabled? Client will need to proceed to 2FA login step first
            if current_user.user_2fa_enabled:
                if current_user.user_2fa_otp_enabled and current_user.user_2fa_otp_secret:
                    response['message'] = gettext('2FA required for this user.')
                    response['redirect_url'] = self._generate_2fa_verification_url()
                else:
                    response['message'] = gettext('2FA enabled but OTP not set for this user. Please setup 2FA.')
                    response['redirect_url'] = self._generate_2fa_setup_url()
            else:
                # Standard Login without 2FA. Check if user is already logged in.
                if args['with_websocket']:
                    self._verify_user_already_logged_in()
                    response['websocket_url'] = self._generate_websocket_url()

                # Generate user token
                response['user_uuid'] = current_user.user_uuid
                response['user_token'] = self._generate_user_token()

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
            return gettext('User already logged in.') + str(e), 403
        except Exception as e:
            # Something went wrong, logout user
            self._user_logout()
            raise e
        else:
            # Everything went well, return response
            self._send_login_success_message()
            return response, 200


    @api.doc(description='Login to the server using HTTP Basic Authentication (HTTPAuth)')
    @api.expect(get_parser)
    @user_http_auth.login_required
    def get(self):
        """
        Login to the server using HTTP Basic Authentication (HTTPAuth)
        """
        return self._common_login_response(get_parser)


    @api.doc(description='Login to the server using HTTP Basic Authentication (HTTPAuth)')
    @api.expect(post_parser)
    @user_http_auth.login_required
    def post(self):
        """
        Login to the server using HTTP Basic Authentication (HTTPAuth)
        """
        return self._common_login_response(post_parser)
