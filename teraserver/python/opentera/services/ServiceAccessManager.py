from werkzeug.local import LocalProxy
from functools import wraps
from flask import _request_ctx_stack, request
from flask_restx import reqparse
from typing import List
from enum import Enum
from flask_babel import gettext
import jwt

from opentera.services.TeraUserClient import TeraUserClient
from opentera.services.TeraDeviceClient import TeraDeviceClient
from opentera.services.TeraParticipantClient import TeraParticipantClient
from opentera.services.TeraServiceClient import TeraServiceClient
from opentera.services.DisabledTokenStorage import DisabledTokenStorage
from opentera.utils.UserAgentParser import UserAgentParser
from opentera.redis.RedisVars import RedisVars
import opentera.messages.python as messages

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
    service = None

    # Only user & participant tokens expire (for now)
    __user_disabled_token_storage = DisabledTokenStorage(redis_key='user_disabled_tokens')
    __participant_disabled_token_storage = DisabledTokenStorage(redis_key='participant_disabled_tokens')

    @staticmethod
    def init_access_manager(service):
        # Set service
        ServiceAccessManager.service = service

        # Update Service Access information
        ServiceAccessManager.api_user_token_key = \
            service.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
        ServiceAccessManager.api_participant_token_key = \
            service.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)
        ServiceAccessManager.api_participant_static_token_key = \
            service.redisGet(RedisVars.RedisVar_ParticipantStaticTokenAPIKey)
        ServiceAccessManager.api_device_token_key = \
            service.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
        ServiceAccessManager.api_device_static_token_key = \
            service.redisGet(RedisVars.RedisVar_DeviceStaticTokenAPIKey)
        ServiceAccessManager.api_service_token_key = \
            service.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)

        # Update Token Storage information
        ServiceAccessManager.__user_disabled_token_storage.config(
            service.config_man, ServiceAccessManager.api_user_token_key)
        ServiceAccessManager.__participant_disabled_token_storage.config(
            service.config_man, ServiceAccessManager.api_participant_token_key)

    @staticmethod
    def user_add_disabled_token(token):
        return ServiceAccessManager.__user_disabled_token_storage.add_disabled_token(token)

    @staticmethod
    def is_user_token_disabled(token):
        return ServiceAccessManager.__user_disabled_token_storage.is_disabled_token(token)

    @staticmethod
    def participant_add_disabled_token(token):
        return ServiceAccessManager.__participant_disabled_token_storage.add_disabled_token(token)

    @staticmethod
    def is_participant_token_disabled(token):
        return ServiceAccessManager.__participant_disabled_token_storage.is_disabled_token(token)

    @staticmethod
    def token_required(allow_dynamic_tokens=True, allow_static_tokens=False):
        def wrap(f):
            def decorated(*args, **kwargs):
                # We support 3 authentication scheme: token in url, cookie and authorization header
                token = None
                login_infos = UserAgentParser.parse_request_for_login_infos(request)

                ######################
                # AUTHORIZATION HEADER
                if 'Authorization' in request.headers:
                    try:
                        # Default whitespace as separator, 1 split max
                        scheme, atoken = request.headers['Authorization'].split(None, 1)
                    except ValueError:
                        # malformed Authorization header
                        ServiceAccessManager.service.logger.send_login_event(
                            sender='ServiceAccessManager.token_required',
                            level=messages.LogEvent.LOGLEVEL_ERROR,
                            login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                            login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                            client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                            client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                            os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'],
                            service_uuid=ServiceAccessManager.service.service_uuid)
                        return gettext('Forbidden'), 403

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
                # USER TOKEN MANAGEMENT
                if allow_dynamic_tokens:  # User only use dynamic tokens, don't validate otherwise
                    if ServiceAccessManager.validate_user_token(token=token):
                        return f(*args, **kwargs)

                # DEVICE TOKEN MANAGEMENT
                if ServiceAccessManager.validate_device_token(token=token, allow_dynamic_tokens=allow_dynamic_tokens,
                                                              allow_static_tokens=allow_static_tokens):
                    return f(*args, **kwargs)

                # PARTICIPANT TOKEN MANAGEMENT
                if ServiceAccessManager.validate_participant_token(token=token,
                                                                   allow_dynamic_tokens=allow_dynamic_tokens,
                                                                   allow_static_tokens=allow_static_tokens):
                    return f(*args, **kwargs)

                ServiceAccessManager.service.logger.send_login_event(
                    sender='ServiceAccessManager.token_required',
                    level=messages.LogEvent.LOGLEVEL_ERROR,
                    login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                    login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                    client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                    client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                    os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'],
                    service_uuid=ServiceAccessManager.service.service_uuid)
                return gettext('Forbidden'), 403

            return decorated
        return wrap

    @staticmethod
    def service_token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # We support token auth. only.
            token = None
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            ######################
            # AUTHORIZATION HEADER
            if 'Authorization' in request.headers:
                try:
                    # Default whitespace as separator, 1 split max
                    scheme, atoken = request.headers['Authorization'].split(None, 1)
                except ValueError:
                    # malformed Authorization header
                    ServiceAccessManager.service.logger.send_login_event(
                        sender='ServiceAccessManager.service_token_required',
                        level=messages.LogEvent.LOGLEVEL_ERROR,
                        login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                        login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                        client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                        client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                        os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'],
                        service_uuid=ServiceAccessManager.service.service_uuid)
                    return gettext('Forbidden'), 403

                # Verify scheme and token
                if scheme == 'OpenTera':
                    token = atoken

            # Verify token from with service api key
            if ServiceAccessManager.validate_service_token(token=token):
                return f(*args, **kwargs)

            ServiceAccessManager.service.logger.send_login_event(
                sender='ServiceAccessManager.service_token_required',
                level=messages.LogEvent.LOGLEVEL_ERROR,
                login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'],
                service_uuid=ServiceAccessManager.service.service_uuid)
            return gettext('Forbidden'), 403

        return decorated

    @staticmethod
    def service_or_others_token_required(allow_dynamic_tokens=True, allow_static_tokens=False):
        def wrap(f):
            def decorated(*args, **kwargs):
                # We support 3 authentication scheme: token in url, cookie and authorization header
                token = None
                login_infos = UserAgentParser.parse_request_for_login_infos(request)
                ######################
                # AUTHORIZATION HEADER
                if 'Authorization' in request.headers:
                    try:
                        # Default whitespace as separator, 1 split max
                        scheme, atoken = request.headers['Authorization'].split(None, 1)
                    except ValueError:
                        # malformed Authorization header
                        ServiceAccessManager.service.logger.send_login_event(
                            sender='ServiceAccessManager.service_or_others_token_required',
                            level=messages.LogEvent.LOGLEVEL_ERROR,
                            login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                            login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                            client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                            client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                            os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'],
                            service_uuid=ServiceAccessManager.service.service_uuid)
                        return gettext('Forbidden'), 403

                    # Verify scheme and token
                    if scheme == 'OpenTera':
                        token = atoken

                        # Service tokens only allowed in authorization header - check here
                        if ServiceAccessManager.validate_service_token(token=token):
                            return f(*args, **kwargs)

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
                # USER TOKEN MANAGEMENT
                if allow_dynamic_tokens:  # User only use dynamic tokens, don't validate otherwise
                    if ServiceAccessManager.validate_user_token(token=token):
                        return f(*args, **kwargs)

                # DEVICE TOKEN MANAGEMENT
                if ServiceAccessManager.validate_device_token(token=token, allow_dynamic_tokens=allow_dynamic_tokens,
                                                              allow_static_tokens=allow_static_tokens):
                    return f(*args, **kwargs)

                # PARTICIPANT TOKEN MANAGEMENT
                if ServiceAccessManager.validate_participant_token(token=token,
                                                                   allow_dynamic_tokens=allow_dynamic_tokens,
                                                                   allow_static_tokens=allow_static_tokens):
                    return f(*args, **kwargs)

                ServiceAccessManager.service.logger.send_login_event(
                    sender='ServiceAccessManager.service_or_others_token_required',
                    level=messages.LogEvent.LOGLEVEL_ERROR,
                    login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                    login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                    client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                    client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                    os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'],
                    service_uuid=ServiceAccessManager.service.service_uuid)
                return gettext('Forbidden'), 403

            return decorated

        return wrap

    @staticmethod
    def validate_user_token(token: str) -> bool:
        try:
            token_dict = jwt.decode(token, ServiceAccessManager.api_user_token_key, algorithms='HS256')
        except jwt.PyJWTError as e:
            # Not a user, or invalid token, will continue...
            pass
        else:
            # Check if token is disabled
            if ServiceAccessManager.is_user_token_disabled(token):
                return False

            # User token is valid and not disabled
            _request_ctx_stack.top.current_user_client = \
                TeraUserClient(token_dict, token, ServiceAccessManager.service.config_man)
            _request_ctx_stack.top.current_login_type = LoginType.USER_LOGIN
            return True

    @staticmethod
    def validate_device_token(token: str, allow_dynamic_tokens: bool, allow_static_tokens: bool) -> bool:
        if allow_dynamic_tokens:  # Check for dynamic device token
            try:
                token_dict = jwt.decode(token, ServiceAccessManager.api_device_token_key, algorithms='HS256')
            except jwt.PyJWTError as e:
                # Not a device, or invalid token, will continue...
                pass
            else:
                # Device token
                _request_ctx_stack.top.current_device_client = \
                    TeraDeviceClient(token_dict, token, ServiceAccessManager.service.config_man)
                _request_ctx_stack.top.current_login_type = LoginType.DEVICE_LOGIN
                return True

        if allow_static_tokens:  # Check for static device token
            try:
                token_dict = jwt.decode(token, ServiceAccessManager.api_device_static_token_key, algorithms='HS256')
            except jwt.PyJWTError as e:
                # Not a device, or invalid token, will continue...
                pass
            else:
                # Device token
                _request_ctx_stack.top.current_device_client = \
                    TeraDeviceClient(token_dict, token, ServiceAccessManager.service.config_man)
                _request_ctx_stack.top.current_login_type = LoginType.DEVICE_LOGIN
                return True

        return False

    @staticmethod
    def validate_participant_token(token: str, allow_dynamic_tokens: bool, allow_static_tokens: bool) -> bool:
        if allow_dynamic_tokens:  # Check for dynamic participant token
            try:
                token_dict = jwt.decode(token, ServiceAccessManager.api_participant_token_key, algorithms='HS256')
            except jwt.PyJWTError as e:
                # Not a participant, or invalid token, will continue...
                pass
            else:
                # Look for disabled tokens, token was decoded successfully
                if ServiceAccessManager.is_participant_token_disabled(token):
                    return False

                # Participant token is not disabled, everything is ok
                _request_ctx_stack.top.current_participant_client = \
                    TeraParticipantClient(token_dict, token, ServiceAccessManager.service.config_man)
                _request_ctx_stack.top.current_login_type = LoginType.PARTICIPANT_LOGIN
                return True

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
                    TeraParticipantClient(token_dict, token, ServiceAccessManager.service.config_man)
                _request_ctx_stack.top.current_login_type = LoginType.PARTICIPANT_LOGIN
                return True

        return False

    @staticmethod
    def validate_service_token(token: str) -> bool:
        try:
            token_dict = jwt.decode(token, ServiceAccessManager.api_service_token_key, algorithms='HS256')
        except jwt.PyJWTError as e:
            # Not a device, or invalid token, will continue...
            pass
        else:
            # Service token
            _request_ctx_stack.top.current_service_client = \
                TeraServiceClient(token_dict, token, ServiceAccessManager.service.config_man)
            _request_ctx_stack.top.current_login_type = LoginType.SERVICE_LOGIN
            return True

        return False

    @staticmethod
    def service_user_roles_required(roles: List[str]):
        def wrap(f):
            @wraps(f)
            def decorated(*args, **kwargs):

                # Check if service is initialized
                if ServiceAccessManager.service is None or 'service_key' \
                        not in ServiceAccessManager.service.service_info:
                    return gettext('Forbidden'), 403

                service_key = ServiceAccessManager.service.service_info['service_key']

                # Check if user is logged in, watch out not None object but LocalProxy cannot use is None...
                if not current_user_client:
                    return gettext('Forbidden'), 403

                # Super admin pass through
                if current_user_client.user_superadmin:
                    return f(*args, **kwargs)

                # Check if user has the required role (global roles are stored in token)
                user_roles_from_token = current_user_client.get_roles_for_service(service_key)

                # Check if user has the required roles
                if not all(role in user_roles_from_token for role in roles):
                    return gettext('Forbidden'), 403

                # Everything ok, continue
                return f(*args, **kwargs)
            return decorated
        return wrap
