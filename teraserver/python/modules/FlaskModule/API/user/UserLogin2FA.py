from flask import session, request
from flask_login import logout_user
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_http_auth, LoginModule, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.FlaskModule.API.user.UserLoginBase import UserLoginBase
from modules.FlaskModule.API.user.UserLoginBase import OutdatedClientVersionError, InvalidClientVersionError, \
    InvalidClientVersionHandlerError, UserAlreadyLoggedInError
from werkzeug.exceptions import BadRequest
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from opentera.utils.UserAgentParser import UserAgentParser

import opentera.messages.python as messages
from opentera.redis.RedisVars import RedisVars
import pyotp
from opentera.db.models.TeraUser import TeraUser

get_parser = api.parser()
get_parser.add_argument('with_websocket', type=inputs.boolean,
                        help='If set, requires that a websocket url is returned.'
                             'If not possible to do so, return a 403 error.',
                        default=False)

get_parser.add_argument('otp_code', type=str, required=True, help='2FA otp code')


class UserLogin2FA(UserLoginBase):

    def __init__(self, _api, *args, **kwargs):
        UserLoginBase.__init__(self, _api, *args, **kwargs)

    @api.doc(description='Login to the server using HTTP Basic Authentication (HTTPAuth) and 2FA')
    @api.expect(get_parser, validate=True)
    @user_http_auth.login_required
    def get(self):
        try:
            args = get_parser.parse_args(strict=True)

            # Current user is logged in with HTTPAuth
            # Let's verify if 2FA is enabled and if OTP is valid
            if not current_user.user_2fa_enabled:
                self._user_logout()
                return gettext('User does not have 2FA enabled'), 403
            if not current_user.user_2fa_otp_enabled or not current_user.user_2fa_otp_secret:
                self._user_logout()
                return gettext('User does not have 2FA OTP enabled or secret set'), 403

            # Verify OTP
            totp = pyotp.TOTP(current_user.user_2fa_otp_secret)
            if not totp.verify(args['otp_code']):
                self._user_logout()
                return gettext('Invalid OTP code'), 403

            # OTP validation completed, proceed with standard login
            response = {}

            version_info = self._verify_client_version()

            if args['with_websocket']:
                self._verify_user_already_logged_in()
                response['websocket_url'] = self._generate_websocket_url()

            # Generate user token
            response['user_uuid'] = current_user.user_uuid
            response['user_token'] = self._generate_user_token()

            if version_info:
                response.update(version_info)

        except OutdatedClientVersionError as e:
            self._user_logout()

            return {
                'version_latest': e.version_latest,
                'current_version': e.current_version,
                'version_error': e.version_error,
                'message': gettext('Client major version too old, not accepting login')}, 426
        except InvalidClientVersionError as e:
            # Invalid client version, will not be handled for now
            pass
        except InvalidClientVersionHandlerError as e:
            self._user_logout()
            return gettext('Invalid client version handler'), 500
        except UserAlreadyLoggedInError as e:
            self._user_logout()
            return gettext('User already logged in.'), 403
        except Exception as e:
            # Something went wrong, logout user
            self._user_logout()
            raise e
        else:
            # Everything went well, return response
            self._send_login_success_message()
            return response, 200




