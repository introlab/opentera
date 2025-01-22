import json
import re

from flask import session, request, Response, redirect
from flask_login import logout_user
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import current_user
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from opentera.utils.UserAgentParser import UserAgentParser
from opentera.utils.TeraVersions import TeraVersions
import opentera.messages.python as messages
from opentera.redis.RedisVars import RedisVars
from opentera.db.models.TeraService import TeraService


class OutdatedClientVersionError(Exception):
    """
    Raised when the client version is too old.
    """
    def __init__(self, message, version_latest=None, current_version=None, version_error=None):
        super().__init__(message)
        self.version_latest = version_latest
        self.current_version = current_version
        self.version_error = version_error


class InvalidClientVersionError(Exception):
    """
    Raised when the client version is invalid.
    """
    def __init__(self, message):
        super().__init__(message)

class UserAlreadyLoggedInError(Exception):
    """
    Raised when the user is already logged in.
    """
    def __init__(self, message):
        super().__init__(message)

class TooMany2FALoginAttemptsError(Exception):
    """
    Raised when the user has too many 2FA login attempts.
    """
    def __init__(self, message):
        super().__init__(message)

class InvalidAuthCodeError(Exception):
    """
    Raised when the authentication code is invalid.
    """
    def __init__(self, message):
        super().__init__(message)


class UserLoginBase(Resource):
    """
    UserLoginBase for all Login resources.
    """

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)
        if self.module:
            self.servername = self.module.config.server_config['hostname']
            self.port = self.module.config.server_config['port']
        else:
            self.servername = 'localhost'
            self.port = 40075

        # Setup servername and port from headers if available
        # This will happen when the server is behind a reverse proxy
        if 'X_EXTERNALSERVER' in request.headers:
            self.servername = request.headers['X_EXTERNALSERVER']
        if 'X_EXTERNALPORT' in request.headers:
            self.port = request.headers['X_EXTERNALPORT']

    def _verify_user_already_logged_in(self) -> None:
        online_users = []
        if not self.test:
            rpc = RedisRPCClient(self.module.config.redis_config)
            online_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_users')

            if current_user.user_uuid in online_users:
                user_agent_info = UserAgentParser.parse_request_for_login_infos(request)
                self.module.logger.send_login_event(sender=self.module.module_name,
                                        level=messages.LogEvent.LOGLEVEL_ERROR,
                                        login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                        login_status=
                                        messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_ALREADY_LOGGED_IN,
                                        client_name=user_agent_info['client_name'],
                                        client_version=user_agent_info['client_version'],
                                        client_ip=user_agent_info['client_ip'],
                                        os_name=user_agent_info['os_name'],
                                        os_version=user_agent_info['os_version'],
                                        user_uuid=current_user.user_uuid,
                                        server_endpoint=user_agent_info['server_endpoint'],
                                        message=gettext('User already logged in :'
                                                        + current_user.user_username))
                raise UserAlreadyLoggedInError(gettext('User already logged in.'))


    def _verify_2fa_login_attempts(self, user_uuid: str) -> None:
        attempts_key_2fa = RedisVars.RedisVar_User2FALoginAttemptKey + user_uuid
        attempts = self.module.redisGet(attempts_key_2fa)
        if attempts is not None:
            attempts = int(attempts)
            if attempts >= 5:
                message = gettext('Too many 2FA attempts. Please wait and try again.')
                self._send_login_failure_message(
                    messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_MAX_ATTEMPTS_REACHED, message)
                raise TooMany2FALoginAttemptsError(message)

    def _verify_auth_code(self) -> dict | None:
        if 'auth_code' not in session:
            return None

        auth_code = session['auth_code']
        auth_infos = self.module.redisGet('service_auth_code_' + auth_code)
        if not auth_infos:
            raise InvalidAuthCodeError(gettext('Invalid authentication code'))

        return json.loads(auth_infos)


    def _verify_client_version(self) -> dict | None:
        reply = {}

        # Extract login information
        user_agent_info = UserAgentParser.parse_request_for_login_infos(request)

        # Extract information
        if 'X-Client-Name' not in request.headers or 'X-Client-Version' not in request.headers:
            # raise InvalidClientVersionError(gettext('Client information missing'))
            return None

        client_name = request.headers['X-Client-Name']
        client_version = request.headers['X-Client-Version']

        client_version_parts = client_version.split('.')

        # Load known version from database.
        versions = TeraVersions()
        versions.load_from_db()

        # Verify if we have client information in DB
        client_info = versions.get_client_version_with_name(client_name)
        if client_info:
            # We have something stored for this client, let's verify version numbers
            # For now, we still allow login even when version mismatch
            # Reply full version information
            reply = {'version_latest': client_info.to_dict()}
            if client_info.version != client_version:
                reply['version_error'] = gettext('Client major version mismatch')
                # If major version mismatch, kill client, first part of the version
                stored_client_version_parts = client_info.version.split('.')
                if len(stored_client_version_parts) and len(client_version_parts):
                    if stored_client_version_parts[0] != client_version_parts[0]:
                        self.module.logger.send_login_event(sender=self.module.module_name,
                                            level=messages.LogEvent.LOGLEVEL_ERROR,
                                            login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                            login_status=
                                            messages.LoginEvent.LOGIN_STATUS_UNKNOWN,
                                            client_name=user_agent_info['client_name'],
                                            client_version=user_agent_info['client_version'],
                                            client_ip=user_agent_info['client_ip'],
                                            os_name=user_agent_info['os_name'],
                                            os_version=user_agent_info['os_version'],
                                            user_uuid=current_user.user_uuid,
                                            server_endpoint=user_agent_info['server_endpoint'],
                                            message=gettext('Client version mismatch'))

                        raise OutdatedClientVersionError(
                            gettext('Client major version too old, not accepting login'),
                            version_latest=reply['version_latest'],
                            current_version=client_version_parts,
                            version_error=reply['version_error'])
        else:
            self.module.logger.send_login_event(sender=self.module.module_name,
                                            level=messages.LogEvent.LOGLEVEL_ERROR,
                                            login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                            login_status=
                                            messages.LoginEvent.LOGIN_STATUS_UNKNOWN,
                                            client_name=user_agent_info['client_name'],
                                            client_version=user_agent_info['client_version'],
                                            client_ip=user_agent_info['client_ip'],
                                            os_name=user_agent_info['os_name'],
                                            os_version=user_agent_info['os_version'],
                                            user_uuid=current_user.user_uuid,
                                            server_endpoint=user_agent_info['server_endpoint'],
                                            message=gettext('Unknown client name :') + client_name)
            # For now, simply log the error, this will allow unknown clients to login
            # raise InvalidClientVersionError(gettext('Invalid client name :') + client_name)
        return reply

    def _generate_websocket_url(self) -> str:
        websocket_url = f"wss://{self.servername}:{str(self.port)}/wss/user?id={session['_id']}"
        # The key is set with an expiration of 60s, will be verified when
        # the websocket is opened in the TwistedModule
        self.module.redisSet(session['_id'], session['_user_id'], ex=60)
        return websocket_url

    def _generate_user_token(self) -> str:
        token_key = self.module.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
        return current_user.get_token(token_key)

    def _generate_2fa_verification_url(self) -> str:
        return "/login_validate_2fa"

    def _generate_2fa_setup_url(self) -> str:
        return "/login_setup_2fa"

    def _generate_login_url(self) -> str:
        return "/login"

    def _generate_password_change_url(self) -> str:
        return "/login_change_password"

    def _user_logout(self):
        logout_user()
        session.clear()

    def _send_login_success_message(self, message: str = ''):
        user_agent_info = UserAgentParser.parse_request_for_login_infos(request)
        self.module.logger.send_login_event(sender=self.module.module_name,
                                            level=messages.LogEvent.LOGLEVEL_INFO,
                                            login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                            login_status=messages.LoginEvent.LOGIN_STATUS_SUCCESS,
                                            client_name=user_agent_info['client_name'],
                                            client_version=user_agent_info['client_version'],
                                            client_ip=user_agent_info['client_ip'],
                                            os_name=user_agent_info['os_name'],
                                            os_version=user_agent_info['os_version'],
                                            user_uuid=current_user.user_uuid,
                                            server_endpoint=user_agent_info['server_endpoint'],
                                            message=message)

    def _send_login_failure_message(self,
                                    status: messages.LoginEvent.LoginStatus, message:str = ''):
        user_agent_info = UserAgentParser.parse_request_for_login_infos(request)
        self.module.logger.send_login_event(sender=self.module.module_name,
                                            level=messages.LogEvent.LOGLEVEL_ERROR,
                                            login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                            login_status=status,
                                            client_name=user_agent_info['client_name'],
                                            client_version=user_agent_info['client_version'],
                                            client_ip=user_agent_info['client_ip'],
                                            os_name=user_agent_info['os_name'],
                                            os_version=user_agent_info['os_version'],
                                            user_uuid=current_user.user_uuid,
                                            server_endpoint=user_agent_info['server_endpoint'],
                                            message=message)

    def _generate_login_success_response(self, with_websocket: bool, base_response: dict) -> Response:
        user_data = base_response
        if with_websocket:
            self._verify_user_already_logged_in()
            user_data['websocket_url'] = self._generate_websocket_url()

        # Generate user token
        user_data['user_uuid'] = current_user.user_uuid
        user_data['user_fullname'] = current_user.get_fullname()
        user_data['user_token'] = self._generate_user_token()

        if 'auth_code' in session:
            # Get information from redis
            try:
                code_infos = self._verify_auth_code()
                # Generate redirect url
                service: TeraService = TeraService.get_service_by_uuid(code_infos['service_uuid'])
                if not service:
                    self._user_logout()
                    return Response(gettext('Invalid service'), status=400)

                endpoint_url = service.service_clientendpoint + '/' + code_infos['endpoint_url'] + '/'
                endpoint_url = re.sub(r'(?<!:)//+', '/', endpoint_url)

            except json.JSONDecodeError:
                self._user_logout()
                return Response(gettext('Invalid authentication code'), status=400)
            except KeyError:
                self._user_logout()
                return Response(gettext('Invalid informations'), status=400)
            else:
                # Redirect to url
                # response = redirect(endpoint_url + '?auth_code=' + session['auth_code'])

                # Add user infos in redis
                auth_infos = self.module.redisGet('service_auth_code_' + session['auth_code'])
                if auth_infos:
                    auth_infos = json.loads(auth_infos)
                    auth_infos['user_data'] = user_data
                    self.module.redisSet('service_auth_code_' + session['auth_code'], json.dumps(auth_infos))

                return {'redirect_url': endpoint_url + '?auth_code=' + session['auth_code']}

        return user_data, 200
