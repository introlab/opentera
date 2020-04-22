from werkzeug.local import LocalProxy
from functools import wraps
from flask import _request_ctx_stack, request, redirect
from flask_restx import reqparse

from enum import Enum

from services.BureauActif.Globals import api_user_token_key, api_device_token_key, api_participant_token_key, \
    TokenCookieName, config_man
from services.shared.TeraUserClient import TeraUserClient
from services.shared.TeraDeviceClient import TeraDeviceClient
from services.shared.TeraParticipantClient import TeraParticipantClient

# Current client identity, stacked
current_user_client = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_user_client', None))
current_device_client = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_device_client', None))
current_participant_client = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_participant_client', None))

current_login_type = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_login_type', LoginType.UNKNOWN_LOGIN))


class LoginType(Enum):
    UNKNOWN_LOGIN = 0,
    USER_LOGIN = 1,
    DEVICE_LOGIN = 2,
    PARTICIPANT_LOGIN = 3


class AccessManager:

    @staticmethod
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # We support 3 authentification scheme: token in url, cookie and authorization header
            token = None
            ######################
            # AUTHORIZATION HEADER
            if 'Authorization' in request.headers:
                try:
                    # Default whitespace as separator, 1 split max
                    scheme, atoken = request.headers['Authorization'].split(None, 1)
                except ValueError:
                    # malformed Authorization header
                    return 'Forbidden', 403

                # Verify scheme and token
                if scheme == 'OpenTera':
                    token = atoken
            else:
                #################
                # TOKEN PARAMETER
                parser = reqparse.RequestParser()
                parser.add_argument('token', type=str, help='Device, participant or user token', required=False)

                # Parse arguments
                request_args = parser.parse_args(strict=False)

                # Verify token in params
                if 'token' in request_args:
                    token = request_args['token']
                else:
                    ###############
                    # COOKIE TOKEN
                    if TokenCookieName in request.cookies:
                        token = request.cookies[TokenCookieName]

            #########################
            # Verify token from redis
            import jwt

            # Do we have a user token?
            try:
                token_dict = jwt.decode(token, api_user_token_key)
            except Exception as e:
                # Not a user, or invalid token, will continue...
                pass
            else:
                # User token
                _request_ctx_stack.top.current_user_client = TeraUserClient(token_dict['user_uuid'], token, config_man)
                _request_ctx_stack.top.current_login_type = LoginType.USER_LOGIN
                return f(*args, **kwargs)

            # Do we have a device token?
            try:
                token_dict = jwt.decode(token, api_device_token_key)
            except Exception as e:
                # Not a device, or invalid token, will continue...
                pass
            else:
                # Device token
                _request_ctx_stack.top.current_device_client = TeraDeviceClient(token_dict['device_uuid'], token,
                                                                                config_man)
                _request_ctx_stack.top.current_login_type = LoginType.DEVICE_LOGIN
                return f(*args, **kwargs)

            # Do we have a participant token?
            try:
                token_dict = jwt.decode(token, api_participant_token_key)
            except Exception as e:
                # Not a participant, or invalid token, will continue...
                pass
            else:
                # Participant token
                _request_ctx_stack.top.current_user_client = TeraParticipantClient(token_dict['participant_uuid'],
                                                                                   token, config_man)
                _request_ctx_stack.top.current_login_type = LoginType.PARTICIPANT_LOGIN
                return f(*args, **kwargs)

            return 'Forbidden', 403

        return decorated
