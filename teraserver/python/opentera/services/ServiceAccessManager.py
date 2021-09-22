from werkzeug.local import LocalProxy
from functools import wraps
from flask import _request_ctx_stack, request
from flask_restx import reqparse

from enum import Enum

from opentera.services.TeraUserClient import TeraUserClient
from opentera.services.TeraDeviceClient import TeraDeviceClient
from opentera.services.TeraParticipantClient import TeraParticipantClient
from opentera.services.TeraServiceClient import TeraServiceClient

# Current client identity, stacked
current_user_client = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_user_client', None))
current_device_client = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_device_client', None))
current_participant_client = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_participant_client', None))
current_service_client = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_service_client', None))


current_login_type = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_login_type', LoginType.UNKNOWN_LOGIN))


class LoginType(Enum):
    UNKNOWN_LOGIN = 0,
    USER_LOGIN = 1,
    DEVICE_LOGIN = 2,
    PARTICIPANT_LOGIN = 3,
    SERVICE_LOGIN = 4


class ServiceAccessManager:

    api_user_token_key = None
    api_participant_token_key = None
    api_participant_static_token_key = None
    api_device_token_key = None
    api_device_static_token_key = None
    api_service_token_key = None
    token_cookie_name = 'OpenTera'
    config_man = None

    @staticmethod
    def token_required(allow_dynamic_tokens=True, allow_static_tokens=False):
        def wrap(f):
            def decorated(*args, **kwargs):
                # We support 3 authentication scheme: token in url, cookie and authorization header
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
                if token is None:
                    #################
                    # TOKEN PARAMETER ?
                    parser = reqparse.RequestParser()
                    parser.add_argument('token', type=str, help='Device, participant or user token', required=False)

                    # Parse arguments
                    request_args = parser.parse_args(strict=False)

                    # Verify token in params
                    if 'token' in request_args:
                        token = request_args['token']
                if token is None:
                    ###############
                    # COOKIE TOKEN
                    if ServiceAccessManager.token_cookie_name in request.cookies:
                        token = request.cookies[ServiceAccessManager.token_cookie_name]

                #########################
                # Verify token from redis
                import jwt

                # USER TOKEN MANAGEMENT
                if allow_dynamic_tokens:  # Users only have dynamic tokens, if the flag isn't set, don't validate token!
                    try:
                        token_dict = jwt.decode(token, ServiceAccessManager.api_user_token_key, algorithms='HS256')
                    except jwt.PyJWTError as e:
                        # Not a user, or invalid token, will continue...
                        pass
                    else:
                        # User token
                        _request_ctx_stack.top.current_user_client = \
                            TeraUserClient(token_dict, token, ServiceAccessManager.config_man)
                        _request_ctx_stack.top.current_login_type = LoginType.USER_LOGIN
                        return f(*args, **kwargs)

                # DEVICE TOKEN MANAGEMENT
                if allow_dynamic_tokens:    # Check for dynamic device token
                    try:
                        token_dict = jwt.decode(token, ServiceAccessManager.api_device_token_key, algorithms='HS256')
                    except jwt.PyJWTError as e:
                        # Not a device, or invalid token, will continue...
                        pass
                    else:
                        # Device token
                        _request_ctx_stack.top.current_device_client = \
                            TeraDeviceClient(token_dict, token, ServiceAccessManager.config_man)
                        _request_ctx_stack.top.current_login_type = LoginType.DEVICE_LOGIN
                        return f(*args, **kwargs)

                if allow_static_tokens:  # Check for static device token
                    try:
                        token_dict = jwt.decode(token, ServiceAccessManager.api_device_static_token_key, algorithms='HS256')
                    except jwt.PyJWTError as e:
                        # Not a device, or invalid token, will continue...
                        pass
                    else:
                        # Device token
                        _request_ctx_stack.top.current_device_client = \
                            TeraDeviceClient(token_dict, token, ServiceAccessManager.config_man)
                        _request_ctx_stack.top.current_login_type = LoginType.DEVICE_LOGIN
                        return f(*args, **kwargs)

                # PARTICIPANT TOKEN MANAGEMENT
                if allow_dynamic_tokens:  # Check for dynamic participant token
                    try:
                        token_dict = jwt.decode(token, ServiceAccessManager.api_participant_token_key, algorithms='HS256')
                    except jwt.PyJWTError as e:
                        # Not a participant, or invalid token, will continue...
                        pass
                    else:
                        # Participant token
                        _request_ctx_stack.top.current_participant_client = \
                            TeraParticipantClient(token_dict, token, ServiceAccessManager.config_man)
                        _request_ctx_stack.top.current_login_type = LoginType.PARTICIPANT_LOGIN
                        return f(*args, **kwargs)

                if allow_static_tokens:  # Check for static participant token
                    try:
                        token_dict = jwt.decode(token, ServiceAccessManager.api_participant_static_token_key,
                                                algorithms='HS256')
                    except jwt.PyJWTError as e:
                        # Not a participant, or invalid token, will continue...
                        pass
                    else:
                        # Participant token
                        _request_ctx_stack.top.current_participant_client = \
                            TeraParticipantClient(token_dict, token, ServiceAccessManager.config_man)
                        _request_ctx_stack.top.current_login_type = LoginType.PARTICIPANT_LOGIN
                        return f(*args, **kwargs)

                return 'Forbidden', 403

            return decorated
        return wrap

    # @staticmethod
    # def static_token_required(f):
    #     @wraps(f)
    #     def decorated(*args, **kwargs):
    #         # We support 3 authentication scheme: token in url, cookie and authorization header
    #         token = None
    #         ######################
    #         # AUTHORIZATION HEADER
    #         if 'Authorization' in request.headers:
    #             try:
    #                 # Default whitespace as separator, 1 split max
    #                 scheme, atoken = request.headers['Authorization'].split(None, 1)
    #             except ValueError:
    #                 # malformed Authorization header
    #                 return 'Forbidden', 403
    #
    #             # Verify scheme and token
    #             if scheme == 'OpenTera':
    #                 token = atoken
    #         if token is None:
    #             #################
    #             # TOKEN PARAMETER ?
    #             parser = reqparse.RequestParser()
    #             parser.add_argument('token', type=str, help='Device, participant or user token', required=False)
    #
    #             # Parse arguments
    #             request_args = parser.parse_args(strict=False)
    #
    #             # Verify token in params
    #             if 'token' in request_args:
    #                 token = request_args['token']
    #
    #         #########################
    #         # Verify token from redis
    #         import jwt
    #
    #         # Do we have a device token?
    #         try:
    #             token_dict = jwt.decode(token, ServiceAccessManager.api_device_static_token_key, algorithms='HS256')
    #         except jwt.PyJWTError as e:
    #             # Not a device, or invalid token, will continue...
    #             pass
    #         else:
    #             # Device token
    #             _request_ctx_stack.top.current_device_client = \
    #                 TeraDeviceClient(token_dict, token, ServiceAccessManager.config_man)
    #             _request_ctx_stack.top.current_login_type = LoginType.DEVICE_LOGIN
    #             return f(*args, **kwargs)
    #
    #         # Do we have a participant token?
    #         try:
    #             token_dict = jwt.decode(token, ServiceAccessManager.api_participant_static_token_key,
    #                                     algorithms='HS256')
    #         except jwt.PyJWTError as e:
    #             # Not a participant, or invalid token, will continue...
    #             pass
    #         else:
    #             # Participant token
    #             _request_ctx_stack.top.current_participant_client = \
    #                 TeraParticipantClient(token_dict, token, ServiceAccessManager.config_man)
    #             _request_ctx_stack.top.current_login_type = LoginType.PARTICIPANT_LOGIN
    #             return f(*args, **kwargs)
    #
    #         return 'Forbidden', 403
    #
    #     return decorated

    @staticmethod
    def service_token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # We support token auth. only.
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

            # Verify token from with service api key
            import jwt

            try:
                token_dict = jwt.decode(token, ServiceAccessManager.api_service_token_key, algorithms='HS256')
            except jwt.PyJWTError as e:
                # Not a device, or invalid token, will continue...
                pass
            else:
                # Service token
                _request_ctx_stack.top.current_service_client = \
                    TeraServiceClient(token_dict, token, ServiceAccessManager.config_man)
                _request_ctx_stack.top.current_login_type = LoginType.SERVICE_LOGIN
                return f(*args, **kwargs)

            return 'Forbidden', 403

        return decorated
