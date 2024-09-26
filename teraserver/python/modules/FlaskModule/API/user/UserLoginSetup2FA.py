from flask import session, request
from flask_login import logout_user
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_http_auth, LoginModule, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.FlaskModule.API.user.UserLoginBase import UserLoginBase
from modules.FlaskModule.API.user.UserLoginBase import OutdatedClientVersionError, InvalidClientVersionError, \
     UserAlreadyLoggedInError
from werkzeug.exceptions import BadRequest
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from opentera.utils.UserAgentParser import UserAgentParser

import opentera.messages.python as messages
from opentera.redis.RedisVars import RedisVars
import pyotp
import pyqrcode
from opentera.db.models.TeraUser import TeraUser

# Get parser
get_parser = api.parser()

# Post parser
post_parser = api.parser()
post_parser.add_argument('otp_secret', type=str, required=True, help='OTP Secret for the user.')
post_parser.add_argument('with_email_enabled', type=inputs.boolean,
                        help='Enable email notifications for 2FA', default=False)


class UserLoginSetup2FA(UserLoginBase):

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
            # Validate args
            args = get_parser.parse_args(strict=True)
            response = {}

            # Current user is logged in with HTTPAuth, or session
            # Let's verify if 2FA is enabled and if OTP is valid
            if not current_user.user_2fa_enabled:
                self._user_logout()
                return gettext('User does not have 2FA enabled'), 403

            if current_user.user_2fa_otp_secret:
                self._user_logout()
                return gettext('User already has 2FA OTP secret set'), 403

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
            return gettext('User already logged in.') + str(e), 403
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
        args = post_parser.parse_args(strict=True)
        return gettext('Not implemented'), 501
