
from flask_login import LoginManager, login_user, logout_user
from flask import session, jsonify

from modules.FlaskModule.FlaskModule import flask_app
from modules.BaseModule import BaseModule, ModuleNames
from modules.RedisVars import RedisVars

from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraService import TeraService

from libtera.ConfigManager import ConfigManager
import datetime
import redis

from flask import current_app, request, jsonify, _request_ctx_stack
from werkzeug.local import LocalProxy
from flask_restx import Resource, reqparse
from functools import wraps

from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

# Current participant identity, stacked
current_participant = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_participant', None))

# Current device identity, stacked
current_device = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_device', None))

# Current user identity, stacked
current_user = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_user', None))

# Current service identity, stacked
current_service = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_service', None))

# Authentication schemes for users
user_http_auth = HTTPBasicAuth(realm='user')
user_token_auth = HTTPTokenAuth("OpenTera")
user_multi_auth = MultiAuth(user_http_auth, user_token_auth)

# Authentication schemes for participant
participant_http_auth = HTTPBasicAuth(realm='participant')
participant_token_auth = HTTPTokenAuth("OpenTera")
participant_multi_auth = MultiAuth(participant_http_auth, participant_token_auth)


class LoginModule(BaseModule):

    redis_client = None

    def __init__(self, config: ConfigManager):

        # Update Global Redis Client
        LoginModule.redis_client = redis.Redis(host=config.redis_config['hostname'],
                                               port=config.redis_config['port'],
                                               db=config.redis_config['db'])

        BaseModule.__init__(self, ModuleNames.LOGIN_MODULE_NAME.value, config)

        self.login_manager = LoginManager()

        # Setup login manager
        self.setup_login_manager()

    def setup_module_pubsub(self):
        # Additional subscribe
        pass

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('LoginModule - Received message ', pattern, channel, message)
        pass

    def setup_login_manager(self):
        self.login_manager.init_app(flask_app)
        self.login_manager.session_protection = "strong"
        # self.login_manager.request_loader(self.load_user)

        # Cookie based configuration
        flask_app.config.update({'REMEMBER_COOKIE_NAME': 'OpenTera',
                                 'REMEMBER_COOKIE_DURATION': 14,
                                 'REMEMBER_COOKIE_SECURE': True,
                                 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(minutes=1),
                                 'REMEMBER_COOKIE_REFRESH_EACH_REQUEST': True})

        # Setup user loader function
        self.login_manager.user_loader(self.load_user)

        # Setup verify password function for users
        user_http_auth.verify_password(self.user_verify_password)
        user_token_auth.verify_token(self.user_verify_token)

        # Setup verify password function for participants
        participant_http_auth.verify_password(self.participant_verify_password)
        participant_token_auth.verify_token(self.participant_verify_token)
        participant_http_auth.get_user_roles(self.participant_get_user_roles_http)
        participant_token_auth.get_user_roles(self.participant_get_user_roles_token)

    def load_user(self, user_id):
        print('LoginModule - load_user', self, user_id)

        # Depending if we have a user or a participant online, return the right object.
        # Here current_user or current_participant are already invalid
        # Need to fetch them from database

        user = TeraUser.get_user_by_uuid(user_id)
        participant = TeraParticipant.get_participant_by_uuid(user_id)

        if participant and user:
            print('ERROR uuid exists for user and participant!')
            # TODO throw exception?
            return None

        if user:
            return user

        if participant:
            return participant

        return None

    def user_verify_password(self, username, password):
        print('LoginModule - user_verify_password ', username)

        if TeraUser.verify_password(username=username, password=password):

            _request_ctx_stack.top.current_user = TeraUser.get_user_by_username(username)

            print('user_verify_password, found user: ', current_user)
            # current_user.update_last_online()

            login_user(current_user, remember=True)
            # print('Setting key with expiration in 60s', session['_id'], session['_user_id'])
            # self.redisSet(session['_id'], session['_user_id'], ex=60)
            return True
        return False

    def user_verify_token(self, token_value):
        """
        Tokens key is dynamic and stored in a redis variable for users.
        """
        import jwt
        try:
            token_dict = jwt.decode(token_value, self.redisGet(RedisVars.RedisVar_UserTokenAPIKey),
                                    algorithms='HS256')
        except jwt.exceptions.PyJWTError as e:
            print(e)
            return False

        if token_dict['user_uuid'] and token_dict['exp']:
            # First verify expiration date
            expiration_date = datetime.datetime.fromtimestamp(token_dict['exp'])

            # Expiration date in the past?
            if expiration_date < datetime.datetime.now():
                return False

            _request_ctx_stack.top.current_user = TeraUser.get_user_by_uuid(token_dict['user_uuid'])
            # TODO: Validate if user is also online?
            if current_user:
                # current_user.update_last_online()
                login_user(current_user, remember=True)
                return True

        return False

    def participant_verify_password(self, username, password):
        print('LoginModule - participant_verify_password for ', username)

        if TeraParticipant.verify_password(username=username, password=password):

            _request_ctx_stack.top.current_participant = TeraParticipant.get_participant_by_username(username)

            print('participant_verify_password, found participant: ', current_participant)
            # current_participant.update_last_online()

            login_user(current_participant, remember=True)

            # Flag that participant has full API access
            current_participant.fullAccess = True

            # print('Setting key with expiration in 60s', session['_id'], session['_user_id'])
            # self.redisSet(session['_id'], session['_user_id'], ex=60)
            return True
        return False

    def participant_verify_token(self, token_value):
        """
        Tokens for participants are stored in the DB.
        """
        print('LoginModule - participant_verify_token for ', token_value, self)

        # TeraParticipant verifies if the participant is active and login is enabled
        _request_ctx_stack.top.current_participant = TeraParticipant.get_participant_by_token(token_value)

        if current_participant:
            # current_participant.update_last_online()
            login_user(current_participant, remember=True)
            return True

        # Second attempt, validate dynamic token
        """
            Tokens key is dynamic and stored in a redis variable for participants.
        """
        import jwt
        try:
            token_dict = jwt.decode(token_value, self.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey),
                                    algorithms='HS256')
        except jwt.exceptions.PyJWTError as e:
            print(e)
            return False

        if token_dict['participant_uuid'] and token_dict['exp']:

            # First verify expiration date
            expiration_date = datetime.datetime.fromtimestamp(token_dict['exp'])

            # Expiration date in the past?
            if expiration_date < datetime.datetime.now():
                return False

            _request_ctx_stack.top.current_participant = \
                TeraParticipant.get_participant_by_uuid(token_dict['participant_uuid'])

        if current_participant:
            # Flag that participant has full API access
            current_participant.fullAccess = True
            # current_participant.update_last_online()
            login_user(current_participant, remember=True)
            return True

        return False

    def participant_get_user_roles_http(self, user):
        # login with username and password will give full access
        if 'username' in user and 'password' in user and current_participant:
            return ['full', 'limited']

        # This should not happen, return no role
        return []

    def participant_get_user_roles_token(self, user):
        # Verify if we have a token auth
        if 'token' in user and current_participant:
            if user['token'] == current_participant.participant_token:
                # Using only "access" token, will give limited access
                return ['limited']
            else:
                # Dynamic token used, need an http login first
                # Token verification is done previously
                return ['full', 'limited']

        # This should not happen, return no role
        return []

    @staticmethod
    def device_token_or_certificate_required(f):
        """
        Use this decorator if UUID is stored in a client certificate or token in url params.
        Acceptable for devices and participants.
        """
        @wraps(f)
        def decorated(*args, **kwargs):

            # Since certificates are more secure than tokens, we will test for them first

            # Headers are modified in TwistedModule to add certificate information if available.
            # We are interested in the content of two fields : X-Device-Uuid, X-Participant-Uuid
            if request.headers.__contains__('X-Device-Uuid'):
                # Load device from DB
                _request_ctx_stack.top.current_device = TeraDevice.get_device_by_uuid(
                    request.headers['X-Device-Uuid'])

                # Device must be found and enabled
                if current_device and current_device.device_enabled:
                    login_user(current_device, remember=True)
                    return f(*args, **kwargs)

            # Then verify tokens...
            # Verify token in auth headers (priority over token in params)
            if 'Authorization' in request.headers:
                try:
                    # Default whitespace as separator, 1 split max
                    scheme, token = request.headers['Authorization'].split(None, 1)
                except ValueError:
                    # malformed Authorization header
                    return 'Invalid token', 401

                # Verify scheme and token
                if scheme == 'OpenTera':
                    # Load device from DB
                    _request_ctx_stack.top.current_device = TeraDevice.get_device_by_token(token)

                    # Device must be found and enabled
                    if current_device and current_device.device_enabled:
                        # Returns the function if authenticated with token
                        login_user(current_device, remember=True)
                        return f(*args, **kwargs)

            # Parse args
            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str, help='Token', required=False)
            token_args = parser.parse_args(strict=False)

            # Verify token in params
            if 'token' in token_args:
                # Load device from DB
                _request_ctx_stack.top.current_device = TeraDevice.get_device_by_token(token_args['token'])

                # Device must be found and enabled
                if current_device and current_device.device_enabled:
                    # Returns the function if authenticated with token
                    login_user(current_device, remember=True)
                    return f(*args, **kwargs)

            # Any other case, do not call function since no valid auth found.
            return 'Unauthorized', 401

        return decorated

    @staticmethod
    def service_token_or_certificate_required(f):
        """
        Use this decorator if UUID is stored in a client certificate or token in url params.
        Acceptable for services
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            import jwt
            # Since certificates are more secure than tokens, we will test for them first
            # Headers are modified in TwistedModule to add certificate information if available.
            # We are interested in the content of field : X-Service-Uuid,
            # if request.headers.__contains__('X-Service-Uuid'):
            #     # Validate service from database
            #     return f(*args, **kwargs)

            # Then verify tokens...
            service_uuid = None
            # Verify token in auth headers (priority over token in params)
            if 'Authorization' in request.headers:
                try:
                    # Default whitespace as separator, 1 split max
                    scheme, token = request.headers['Authorization'].split(None, 1)
                except ValueError:
                    # malformed Authorization header
                    return 'Invalid Token', 401

                # Verify scheme and token
                if scheme == 'OpenTera':

                    try:
                        token_dict = jwt.decode(token,
                                                LoginModule.redis_client.get(
                                                    RedisVars.RedisVar_ServiceTokenAPIKey),
                                                algorithms='HS256')
                        if 'service_uuid' in token_dict:
                            service_uuid = token_dict['service_uuid']
                    except jwt.exceptions.PyJWTError as e:
                        return 'Unauthorized', 401

            # Parse args
            if not service_uuid:
                parser = reqparse.RequestParser()
                parser.add_argument('token', type=str, help='Token', required=False)
                token_args = parser.parse_args(strict=False)

                # Verify token in params
                if token_args['token']:
                    try:
                        token_dict = jwt.decode(token_args['token'],
                                                LoginModule.redis_client.get(
                                                    RedisVars.RedisVar_ServiceTokenAPIKey),
                                                algorithms='HS256')
                        if 'service_uuid' in token_dict:
                            service_uuid = token_dict['service_uuid']
                    except jwt.exceptions.PyJWTError as e:
                        return 'Unauthorized', 401

            if service_uuid:
                # Check if service is allowed to connect
                service = TeraService.get_service_by_uuid(service_uuid)
                if service and service.service_enabled:
                    _request_ctx_stack.top.current_service = service
                    return f(*args, **kwargs)

            # Any other case, do not call function since no valid auth found.
            return 'Unauthorized', 401

        return decorated
