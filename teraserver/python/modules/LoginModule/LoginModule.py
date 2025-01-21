from flask_login import LoginManager, login_user

from modules.FlaskModule.FlaskModule import flask_app
from opentera.modules.BaseModule import BaseModule, ModuleNames
from opentera.redis.RedisVars import RedisVars

from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraService import TeraService

import opentera.messages.python as messages

from opentera.config.ConfigManager import ConfigManager
from opentera.services.DisabledTokenStorage import DisabledTokenStorage
import datetime
import redis

from flask import request, g, session, abort
from flask_babel import gettext
from werkzeug.local import LocalProxy
from flask_restx import reqparse
from functools import wraps, partial

from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth, Authorization

from twisted.internet import task

import modules.Globals as Globals
from opentera.utils.UserAgentParser import UserAgentParser

# Current participant identity, stacked
current_participant = LocalProxy(lambda: g.setdefault('current_participant', None))

# Current device identity, stacked
current_device = LocalProxy(lambda: g.setdefault('current_device', None))

# Current user identity, stacked
current_user = LocalProxy(lambda: g.setdefault('current_user', None))

# Current service identity, stacked
current_service = LocalProxy(lambda: g.setdefault('current_service', None))

# Authentication schemes for users
user_http_auth = HTTPBasicAuth(realm='user')
user_http_login_auth = HTTPBasicAuth(realm='user')
user_token_auth = HTTPTokenAuth("OpenTera")
user_multi_auth = MultiAuth(user_http_auth, user_token_auth)

# Authentication schemes for participant
participant_http_auth = HTTPBasicAuth(realm='participant')
participant_token_auth = HTTPTokenAuth("OpenTera")
participant_multi_auth = MultiAuth(participant_http_auth, participant_token_auth)


class LoginModule(BaseModule):
    # This client is required for static functions
    redis_client = None

    # Only user & participant tokens expire (for now)
    __user_disabled_token_storage = DisabledTokenStorage(redis_key='user_disabled_tokens')
    __participant_disabled_token_storage = DisabledTokenStorage(redis_key='participant_disabled_tokens')

    def __init__(self, config: ConfigManager, app=flask_app):
        self.app = app
        # Update Global Redis Client
        LoginModule.redis_client = redis.Redis(host=config.redis_config['hostname'],
                                               port=config.redis_config['port'],
                                               username=config.redis_config['username'],
                                               password=config.redis_config['password'],
                                               db=config.redis_config['db'])

        # Configure Disabled Token Storage
        LoginModule.__user_disabled_token_storage.config(config, self.redis_client.get(
            RedisVars.RedisVar_UserTokenAPIKey))

        LoginModule.__participant_disabled_token_storage.config(config, self.redis_client.get(
            RedisVars.RedisVar_ParticipantTokenAPIKey))

        BaseModule.__init__(self, ModuleNames.LOGIN_MODULE_NAME.value, config)

        self.login_manager = LoginManager()

        # Setup login manager
        self.setup_login_manager()

        # Setup cleanup task for disabled tokens
        self.cleanup_disabled_tokens_loop_task = task.LoopingCall(self.cleanup_disabled_tokens)

    def cleanup_disabled_tokens(self):
        print('LoginModule.cleanup_disabled_tokens task')
        # Remove expired tokens from user tokens disabled storage
        LoginModule.__user_disabled_token_storage.remove_all_expired_tokens(
            self.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
        )
        # Remove expired tokens from participant tokens disabled storage
        LoginModule.__participant_disabled_token_storage.remove_all_expired_tokens(
            self.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)
        )

    def setup_module_pubsub(self):
        # Additional subscribe here

        # We wait until we are connected to redis
        # Every 30 minutes?
        self.cleanup_disabled_tokens_loop_task.start(60.0 * 30)

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('LoginModule - Received message ', pattern, channel, message)
        pass

    def setup_login_manager(self):
        self.login_manager.init_app(self.app)
        self.login_manager.session_protection = "strong"

        # Cookie based configuration
        self.app.config.update({'REMEMBER_COOKIE_NAME': 'OpenTera',
                                'REMEMBER_COOKIE_DURATION': datetime.timedelta(minutes=30),
                                'REMEMBER_COOKIE_SECURE': True,
                                'REMEMBER_COOKIE_SAMESITE': 'Strict',
                                # 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(minutes=1),
                                # 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(minutes=5),
                                'REMEMBER_COOKIE_REFRESH_EACH_REQUEST': True
                                })

        # Setup user loader function
        self.login_manager.user_loader(self.load_user)

        # Setup verify password function for users
        user_http_auth.verify_password(partial(self.user_verify_password, is_login=False))
        user_http_login_auth.verify_password(partial(self.user_verify_password, is_login=True))
        user_token_auth.verify_token(self.user_verify_token)
        user_http_auth.error_handler(self.auth_error)
        user_http_login_auth.error_handler(self.auth_error)
        user_token_auth.error_handler(self.auth_error)

        # Setup verify password function for participants
        participant_http_auth.verify_password(self.participant_verify_password)
        participant_token_auth.verify_token(self.participant_verify_token)
        participant_http_auth.get_user_roles(self.participant_get_user_roles_http)
        participant_token_auth.get_user_roles(self.participant_get_user_roles_token)
        participant_token_auth.error_handler(self.auth_error)
        participant_http_auth.error_handler(self.auth_error)

    def load_user(self, user_id):
        # print('LoginModule - load_user', self, user_id)
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

    def user_verify_password(self, username, password, is_login):
        # print('LoginModule - user_verify_password', username)
        tentative_user = TeraUser.get_user_by_username(username)
        if not tentative_user:
            # self.logger.log_warning(self.module_name, 'Invalid username', username)
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            self.logger.send_login_event(sender='LoginModule.user_verify_password',
                                         level=messages.LogEvent.LOGLEVEL_ERROR,
                                         login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                         login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_WRONG_USERNAME,
                                         client_name=login_infos['client_name'],
                                         client_version=login_infos['client_version'],
                                         client_ip=login_infos['client_ip'],
                                         os_name=login_infos['os_name'],
                                         os_version=login_infos['os_version'],
                                         message=username,
                                         server_endpoint=login_infos['server_endpoint'])
            return False

        attempts_key = RedisVars.RedisVar_UserLoginAttemptKey + tentative_user.user_uuid
        # Count login attempts
        current_attempts = self.redisGet(attempts_key)
        if not current_attempts:
            current_attempts = 0
        else:
            current_attempts = int(current_attempts)

        if current_attempts >= 5:
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            self.logger.send_login_event(sender='LoginModule.user_verify_password',
                                         level=messages.LogEvent.LOGLEVEL_ERROR,
                                         login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                         login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_MAX_ATTEMPTS_REACHED,
                                         client_name=login_infos['client_name'],
                                         client_version=login_infos['client_version'],
                                         client_ip=login_infos['client_ip'],
                                         os_name=login_infos['os_name'],
                                         os_version=login_infos['os_version'],
                                         user_uuid=tentative_user.user_uuid,
                                         server_endpoint=login_infos['server_endpoint'])
            return False  # Too many attempts in a short period of time will result in temporary disabling (see below)

        logged_user = TeraUser.verify_password(username=username, password=password, user=tentative_user)

        if logged_user and logged_user.is_active():

            if not is_login:
                if logged_user.user_force_password_change:
                    # Prevent API access if password change was requested for that user
                    abort(401, gettext('Unauthorized - User must login first to change password'))
                if logged_user.user_2fa_enabled:
                    # Prevent API access with username/password if 2FA is enabled
                    abort(401, gettext('Unauthorized - 2FA is enabled, must login first and use token'))

            g.current_user = logged_user

            # print('user_verify_password, found user:', current_user)
            current_user.update_last_online()

            # Clear attempts counter
            self.redisDelete(attempts_key)

            login_user(current_user, remember=False)
            # print('Setting key with expiration in 60s', session['_id'], session['_user_id'])
            # self.redisSet(session['_id'], session['_user_id'], ex=60)
            return True

        # Update login attempt count
        current_attempts += 1
        self.redisSet(attempts_key, current_attempts, 120)

        # self.logger.log_warning(self.module_name, 'Invalid password for user', username)
        login_infos = UserAgentParser.parse_request_for_login_infos(request)
        if not tentative_user.is_active():
            login_status = messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_DISABLED_ACCOUNT
        else:
            login_status = messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_WRONG_PASSWORD
        self.logger.send_login_event(sender='LoginModule.user_verify_password',
                                     level=messages.LogEvent.LOGLEVEL_ERROR,
                                     login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                     login_status=login_status,
                                     client_name=login_infos['client_name'],
                                     client_version=login_infos['client_version'],
                                     client_ip=login_infos['client_ip'],
                                     os_name=login_infos['os_name'],
                                     os_version=login_infos['os_version'],
                                     user_uuid=tentative_user.user_uuid,
                                     server_endpoint=login_infos['server_endpoint'])
        return False

    @staticmethod
    def user_add_disabled_token(token):
        LoginModule.__user_disabled_token_storage.add_disabled_token(token)

    @staticmethod
    def is_user_token_disabled(token):
        return LoginModule.__user_disabled_token_storage.is_disabled_token(token)

    def user_verify_token(self, token_value):
        """
        Tokens key is dynamic and stored in a redis variable for users.
        """
        # if not token_value:
        #     return False
        # Disabled tokens should never be used
        if LoginModule.is_user_token_disabled(token_value):
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            self.logger.send_login_event(sender='LoginModule.user_verify_token',
                                         level=messages.LogEvent.LOGLEVEL_ERROR,
                                         login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                                         login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                                         client_name=login_infos['client_name'],
                                         client_version=login_infos['client_version'],
                                         client_ip=login_infos['client_ip'],
                                         os_name=login_infos['os_name'],
                                         os_version=login_infos['os_version'],
                                         message='disabled:' + token_value,  # TODO: Don't store the token?
                                         server_endpoint=login_infos['server_endpoint'])
            return False

        import jwt
        try:
            token_dict = jwt.decode(token_value, self.redisGet(RedisVars.RedisVar_UserTokenAPIKey),
                                    algorithms='HS256')
        except jwt.exceptions.PyJWTError as e:
            # print(e)
            # self.logger.log_error(self.module_name, 'User Token exception occurred')
            if not token_value:
                token_value = ''
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            self.logger.send_login_event(sender='LoginModule.user_verify_token',
                                         level=messages.LogEvent.LOGLEVEL_ERROR,
                                         login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                                         login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                                         client_name=login_infos['client_name'],
                                         client_version=login_infos['client_version'],
                                         client_ip=login_infos['client_ip'],
                                         os_name=login_infos['os_name'],
                                         os_version=login_infos['os_version'],
                                         message=token_value,  # TODO: Don't store the token?
                                         server_endpoint=login_infos['server_endpoint'])
            return False

        if token_dict['user_uuid'] and token_dict['exp']:
            # First verify expiration date
            expiration_date = datetime.datetime.fromtimestamp(token_dict['exp'])

            # Expiration date in the past?
            if expiration_date < datetime.datetime.now():
                # self.logger.log_warning(self.module_name, 'Token expired for user', token_dict['user_uuid'])
                login_infos = UserAgentParser.parse_request_for_login_infos(request)
                self.logger.send_login_event(sender='LoginModule.user_verify_token',
                                             level=messages.LogEvent.LOGLEVEL_ERROR,
                                             login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                                             login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_EXPIRED_TOKEN,
                                             client_name=login_infos['client_name'],
                                             client_version=login_infos['client_version'],
                                             client_ip=login_infos['client_ip'],
                                             os_name=login_infos['os_name'],
                                             os_version=login_infos['os_version'],
                                             user_uuid=token_dict['user_uuid'],
                                             server_endpoint=login_infos['server_endpoint'])
                return False

            g.current_user = TeraUser.get_user_by_uuid(token_dict['user_uuid'])
            # TODO: Validate if user is also online?
            if current_user and current_user.is_active():
                # current_user.update_last_online()
                login_user(current_user, remember=False)
                return True

            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            self.logger.send_login_event(sender='LoginModule.user_verify_token',
                                         level=messages.LogEvent.LOGLEVEL_ERROR,
                                         login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                                         login_status=messages.LoginEvent.LOGIN_STATUS_UNKNOWN if not current_user
                                         else messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_DISABLED_ACCOUNT,
                                         client_name=login_infos['client_name'],
                                         client_version=login_infos['client_version'],
                                         client_ip=login_infos['client_ip'],
                                         os_name=login_infos['os_name'],
                                         os_version=login_infos['os_version'],
                                         user_uuid=token_dict['user_uuid'],
                                         server_endpoint=login_infos['server_endpoint'])

        return False

    def participant_verify_password(self, username, password):
        # print('LoginModule - participant_verify_password for', username)

        tentative_participant = TeraParticipant.get_participant_by_username(username)
        if not tentative_participant:
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            self.logger.send_login_event(sender='LoginModule.participant_verify_password',
                                         level=messages.LogEvent.LOGLEVEL_ERROR,
                                         login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                         login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_WRONG_USERNAME,
                                         client_name=login_infos['client_name'],
                                         client_version=login_infos['client_version'],
                                         client_ip=login_infos['client_ip'],
                                         os_name=login_infos['os_name'],
                                         os_version=login_infos['os_version'],
                                         message=username,
                                         server_endpoint=login_infos['server_endpoint'])
            # self.logger.log_warning(self.module_name, 'Invalid username', username)
            return False

        attempts_key = RedisVars.RedisVar_ParticipantLoginAttemptKey + tentative_participant.participant_uuid
        # Count login attempts
        current_attempts = self.redisGet(attempts_key)
        if not current_attempts:
            current_attempts = 0
        else:
            current_attempts = int(current_attempts)

        if current_attempts >= 5:
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            self.logger.send_login_event(sender='LoginModule.participant_verify_password',
                                         level=messages.LogEvent.LOGLEVEL_ERROR,
                                         login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                         login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_MAX_ATTEMPTS_REACHED,
                                         client_name=login_infos['client_name'],
                                         client_version=login_infos['client_version'],
                                         client_ip=login_infos['client_ip'],
                                         os_name=login_infos['os_name'],
                                         os_version=login_infos['os_version'],
                                         participant_uuid=tentative_participant.participant_uuid,
                                         server_endpoint=login_infos['server_endpoint'])
            return False  # Too many attempts in a short period of time will result in temporary disabling (see below)

        logged_participant = TeraParticipant.verify_password(username=username, password=password,
                                                             participant=tentative_participant)
        if logged_participant and logged_participant.is_active():
            g.current_participant = TeraParticipant.get_participant_by_username(username)

            # print('participant_verify_password, found participant: ', current_participant)
            # current_participant.update_last_online()

            login_user(current_participant, remember=False)

            # Flag that participant has full API access
            g.current_participant.fullAccess = True

            # Clear attempts counter
            self.redisDelete(attempts_key)

            # print('Setting key with expiration in 60s', session['_id'], session['_user_id'])
            # self.redisSet(session['_id'], session['_user_id'], ex=60)
            return True

        # Update login attempt count
        current_attempts += 1
        self.redisSet(attempts_key, current_attempts, 120)

        # self.logger.log_warning(self.module_name, 'Invalid password for participant', username)
        login_infos = UserAgentParser.parse_request_for_login_infos(request)
        self.logger.send_login_event(sender='LoginModule.participant_verify_password',
                                     level=messages.LogEvent.LOGLEVEL_ERROR,
                                     login_type=messages.LoginEvent.LOGIN_TYPE_PASSWORD,
                                     login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_WRONG_PASSWORD if
                                     not logged_participant else
                                     messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_DISABLED_ACCOUNT,
                                     client_name=login_infos['client_name'],
                                     client_version=login_infos['client_version'],
                                     client_ip=login_infos['client_ip'],
                                     os_name=login_infos['os_name'],
                                     os_version=login_infos['os_version'],
                                     participant_uuid=tentative_participant.participant_uuid,
                                     server_endpoint=login_infos['server_endpoint'])

        return False

    @staticmethod
    def participant_add_disabled_token(token):
        LoginModule.__participant_disabled_token_storage.add_disabled_token(token)

    @staticmethod
    def is_participant_token_disabled(token):
        return LoginModule.__participant_disabled_token_storage.is_disabled_token(token)

    def participant_verify_token(self, token_value):
        """
        Tokens for participants are stored in the DB.
        """
        # print('LoginModule - participant_verify_token for ', token_value, self)

        # TeraParticipant verifies if the participant is active and login is enabled
        g.current_participant = TeraParticipant.get_participant_by_token(token_value)

        if current_participant and current_participant.is_active():
            # current_participant.update_last_online()
            g.current_participant.fullAccess = False
            login_user(current_participant, remember=False)
            return True

        # Second attempt, validate dynamic token
        if not token_value:
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            self.logger.send_login_event(sender='LoginModule.participant_verify_token',
                                         level=messages.LogEvent.LOGLEVEL_ERROR,
                                         login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                                         login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                                         client_name=login_infos['client_name'],
                                         client_version=login_infos['client_version'],
                                         client_ip=login_infos['client_ip'],
                                         os_name=login_infos['os_name'],
                                         os_version=login_infos['os_version'],
                                         message='no token specified',
                                         server_endpoint=login_infos['server_endpoint'])
            return False

        # Disabled tokens should never be used
        if LoginModule.is_participant_token_disabled(token_value):
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            self.logger.send_login_event(sender='LoginModule.participant_verify_token',
                                         level=messages.LogEvent.LOGLEVEL_ERROR,
                                         login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                                         login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                                         client_name=login_infos['client_name'],
                                         client_version=login_infos['client_version'],
                                         client_ip=login_infos['client_ip'],
                                         os_name=login_infos['os_name'],
                                         os_version=login_infos['os_version'],
                                         message='disabled:' + token_value,  # TODO: Don't store the token?
                                         server_endpoint=login_infos['server_endpoint'])
            return False

        """
            Tokens key is dynamic and stored in a redis variable for participants.
        """
        import jwt
        try:
            token_dict = jwt.decode(token_value, self.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey),
                                    algorithms='HS256', options={"verify_jti": False})
        except jwt.exceptions.PyJWTError as e:
            # print(e)
            # self.logger.log_error(self.module_name, 'Participant Token exception occurred')
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            self.logger.send_login_event(sender='LoginModule.participant_verify_token',
                                         level=messages.LogEvent.LOGLEVEL_ERROR,
                                         login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                                         login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                                         client_name=login_infos['client_name'],
                                         client_version=login_infos['client_version'],
                                         client_ip=login_infos['client_ip'],
                                         os_name=login_infos['os_name'],
                                         os_version=login_infos['os_version'],
                                         message=token_value,  # TODO: Don't store the token?
                                         server_endpoint=login_infos['server_endpoint'])
            return False

        if token_dict['participant_uuid'] and token_dict['exp']:

            # First verify expiration date
            expiration_date = datetime.datetime.fromtimestamp(token_dict['exp'])

            # Expiration date in the past?
            if expiration_date < datetime.datetime.now():
                # self.logger.log_warning(self.module_name, 'Token expired for participant',
                #                         token_dict['participant_uuid'])
                login_infos = UserAgentParser.parse_request_for_login_infos(request)
                self.logger.send_login_event(sender='LoginModule.participant_verify_token',
                                             level=messages.LogEvent.LOGLEVEL_ERROR,
                                             login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                                             login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_EXPIRED_TOKEN,
                                             client_name=login_infos['client_name'],
                                             client_version=login_infos['client_version'],
                                             client_ip=login_infos['client_ip'],
                                             os_name=login_infos['os_name'],
                                             os_version=login_infos['os_version'],
                                             participant_uuid=token_dict['participant_uuid'],
                                             server_endpoint=login_infos['server_endpoint'])
                return False

            g.current_participant = \
                TeraParticipant.get_participant_by_uuid(token_dict['participant_uuid'])

        if current_participant and current_participant.is_active():
            # Flag that participant has full API access
            g.current_participant.fullAccess = True
            # current_participant.update_last_online()
            login_user(current_participant, remember=False)
            return True

        login_infos = UserAgentParser.parse_request_for_login_infos(request)
        self.logger.send_login_event(sender='LoginModule.participant_verify_token',
                                     level=messages.LogEvent.LOGLEVEL_ERROR,
                                     login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                                     login_status=messages.LoginEvent.LOGIN_STATUS_UNKNOWN,
                                     client_name=login_infos['client_name'],
                                     client_version=login_infos['client_version'],
                                     client_ip=login_infos['client_ip'],
                                     os_name=login_infos['os_name'],
                                     os_version=login_infos['os_version'],
                                     participant_uuid=token_dict['participant_uuid'],
                                     server_endpoint=login_infos['server_endpoint'])
        return False

    def participant_get_user_roles_http(self, user):
        # login with username and password will give full access
        if 'username' in user and 'password' in user and current_participant:
            return ['full', 'limited']

        # This should not happen, return no role
        return []

    def participant_get_user_roles_token(self, user):
        # Verify if we have a token auth
        token = None
        if isinstance(user, Authorization):
            # Authorization header, not a token parameter
            token = user.token
        elif 'token' in user:
            token = user['token']
        if token and current_participant:
            if token == current_participant.participant_token:
                # Using only "access" token, will give limited access
                return ['limited']
            else:
                # Dynamic token used, need an http login first
                # Token verification is done previously
                return ['full', 'limited']

        # This should not happen, return no role
        return []

    @staticmethod
    def auth_error(status):
        return gettext("Unauthorized"), status

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
                g.current_device = TeraDevice.get_device_by_uuid(
                    request.headers['X-Device-Uuid'])

                # Device must be found and enabled
                if current_device:
                    if current_device.device_enabled:
                        login_user(current_device, remember=False)
                        return f(*args, **kwargs)
                    else:
                        login_infos = UserAgentParser.parse_request_for_login_infos(request)
                        Globals.login_module.logger.send_login_event(
                            sender='LoginModule.device_token_or_certificate_required',
                            level=messages.LogEvent.LOGLEVEL_ERROR,
                            login_type=messages.LoginEvent.LOGIN_TYPE_CERTIFICATE,
                            login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_DISABLED_ACCOUNT,
                            client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                            client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                            os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'])
                        return gettext('Disabled device'), 401

            # Then verify tokens...
            # Verify token in auth headers (priority over token in params)
            if 'Authorization' in request.headers:
                try:
                    # Default whitespace as separator, 1 split max
                    scheme, token = request.headers['Authorization'].split(None, 1)
                except ValueError:
                    # malformed Authorization header
                    return gettext('Invalid token'), 401

                # Verify scheme and token
                if scheme == 'OpenTera':
                    # Load device from DB
                    g.current_device = TeraDevice.get_device_by_token(token)

                    # Device must be found and enabled
                    if current_device:
                        if current_device.device_enabled:
                            # Returns the function if authenticated with token
                            login_user(current_device, remember=False)
                            return f(*args, **kwargs)
                        else:
                            login_infos = UserAgentParser.parse_request_for_login_infos(request)
                            Globals.login_module.logger.send_login_event(
                                sender='LoginModule.device_token_or_certificate_required',
                                level=messages.LogEvent.LOGLEVEL_ERROR,
                                login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                                login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_DISABLED_ACCOUNT,
                                client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                                client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                                os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'])
                            return gettext('Disabled device'), 401

            # Parse args
            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str, help='Token', required=False)
            token_args = parser.parse_args(strict=False)

            # Verify token in params
            if 'token' in token_args:
                # Load device from DB
                g.current_device = TeraDevice.get_device_by_token(token_args['token'])

                # Device must be found and enabled
                if current_device and current_device.device_enabled:
                    # Returns the function if authenticated with token
                    login_user(current_device, remember=False)
                    return f(*args, **kwargs)

            # Any other case, do not call function since no valid auth found.
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            if request.headers.__contains__('X-Device-Uuid'):
                login_type = messages.LoginEvent.LOGIN_TYPE_CERTIFICATE
            else:
                login_type = messages.LoginEvent.LOGIN_TYPE_TOKEN
            Globals.login_module.logger.send_login_event(
                sender='LoginModule.device_token_or_certificate_required',
                level=messages.LogEvent.LOGLEVEL_ERROR,
                login_type=login_type,
                login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'])
            return gettext('Unauthorized'), 401

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
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            if request.headers.__contains__('X-Service-Uuid'):
                login_type = messages.LoginEvent.LOGIN_TYPE_CERTIFICATE
            else:
                login_type = messages.LoginEvent.LOGIN_TYPE_TOKEN

            # Verify token in auth headers (priority over token in params)
            if 'Authorization' in request.headers:
                try:
                    # Default whitespace as separator, 1 split max
                    scheme, token = request.headers['Authorization'].split(None, 1)
                except ValueError:
                    # malformed Authorization header
                    Globals.login_module.logger.send_login_event(
                        sender='LoginModule.service_token_or_certificate_required',
                        level=messages.LogEvent.LOGLEVEL_ERROR,
                        login_type=login_type,
                        login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                        client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                        client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                        os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'],
                        service_uuid=service_uuid)
                    return gettext('Invalid Token'), 401

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
                        Globals.login_module.logger.send_login_event(
                            sender='LoginModule.service_token_or_certificate_required',
                            level=messages.LogEvent.LOGLEVEL_ERROR,
                            login_type=login_type,
                            login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                            client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                            client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                            os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'],
                            service_uuid=service_uuid)
                        return gettext('Unauthorized'), 401

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
                        Globals.login_module.logger.send_login_event(
                            sender='LoginModule.service_token_or_certificate_required',
                            level=messages.LogEvent.LOGLEVEL_ERROR,
                            login_type=login_type,
                            login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                            client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                            client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                            os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'],
                            service_uuid=service_uuid)
                        return gettext('Unauthorized'), 401

            if service_uuid:
                # Check if service is allowed to connect
                service = TeraService.get_service_by_uuid(service_uuid)
                if service and service.service_enabled:
                    g.current_service = service
                    return f(*args, **kwargs)

            # Any other case, do not call function since no valid auth found.
            Globals.login_module.logger.send_login_event(
                sender='LoginModule.service_token_or_certificate_required',
                level=messages.LogEvent.LOGLEVEL_ERROR,
                login_type=login_type,
                login_status=messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_INVALID_TOKEN,
                client_name=login_infos['client_name'], client_version=login_infos['client_version'],
                client_ip=login_infos['client_ip'], os_name=login_infos['os_name'],
                os_version=login_infos['os_version'], server_endpoint=login_infos['server_endpoint'],
                service_uuid=service_uuid)
            return gettext('Unauthorized'), 401

        return decorated

    @staticmethod
    def user_session_required(f):
        """
        Use this decorator if a user session is required. A session is created when a user logs in. The session contains
        the user UUID.
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            if '_user_id' in session:
                # Verify if we have a valid user
                user = TeraUser.get_user_by_uuid(session['_user_id'])
                if user and user.user_enabled:
                    g.current_user = user
                    return f(*args, **kwargs)
                else:
                    return gettext('Unauthorized'), 401
            else:
                return gettext('Unauthorized'), 401

        return decorated

