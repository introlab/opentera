
from flask_login import LoginManager, login_user, logout_user
from flask import session, jsonify

from modules.FlaskModule.FlaskModule import flask_app
from modules.BaseModule import BaseModule, ModuleNames
from modules.Globals import TeraServerConstants

from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraDevice import TeraDevice

from libtera.ConfigManager import ConfigManager
import datetime

from flask import current_app, request, jsonify, _request_ctx_stack
from werkzeug.local import LocalProxy
from flask_restplus import Resource, reqparse
from functools import wraps

from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

# Current participant identity, stacked
current_participant = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_participant', None))

# Current device identity, stacked
current_device = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_device', None))

# Current user identity, stacked
current_user = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_user', None))

# Authentication schemes for users
user_http_auth = HTTPBasicAuth(realm='user')
user_token_auth = HTTPTokenAuth("OpenTera")
user_multi_auth = MultiAuth(user_http_auth, user_token_auth)

# Authentication schemes for participant
participant_http_auth = HTTPBasicAuth(realm='participant')
participant_token_auth = HTTPTokenAuth("OpenTera")
participant_multi_auth = MultiAuth(participant_http_auth, participant_token_auth)


class LoginModule(BaseModule):

    def __init__(self, config: ConfigManager):

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
            current_user.update_last_online()

            login_user(current_user, remember=True)
            print('Setting key with expiration in 60s', session['_id'], session['_user_id'])

            self.redisSet(session['_id'], session['_user_id'], ex=60)
            return True
        return False

    def user_verify_token(self, token_value):
        """
        Tokens key is dynamic and stored in a redis variable for users.
        """
        import jwt
        try:
            token_dict = jwt.decode(token_value, self.redisGet(TeraServerConstants.RedisVar_UserTokenAPIKey),
                                    algorithms='HS256')
        except jwt.exceptions.InvalidSignatureError as e:
            print(e)
            return False

        if token_dict['user_uuid']:
            _request_ctx_stack.top.current_user = TeraUser.get_user_by_uuid(token_dict['user_uuid'])
            # TODO: Validate if user is also online?
            if current_user:
                current_user.update_last_online()
                login_user(current_user, remember=True)
                # TODO: Set user online in Redis??
                return True

        return False

    def participant_verify_password(self, username, password):
        print('LoginModule - participant_verify_password for ', username)

        if TeraParticipant.verify_password(username=username, password=password):

            _request_ctx_stack.top.current_participant = TeraParticipant.get_participant_by_username(username)

            print('participant_verify_password, found user: ', current_participant)
            current_participant.update_last_online()

            login_user(current_participant, remember=True)
            print('Setting key with expiration in 60s', session['_id'], session['_user_id'])

            self.redisSet(session['_id'], session['_user_id'], ex=60)
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
            current_participant.update_last_online()
            login_user(current_participant, remember=True)
            # TODO: Set user online in Redis??
            return True

        return False

    @staticmethod
    def token_required(f):
        """
        Use this decorator for token in url as param.
        Acceptable for devices and participants.
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            # Parse args
            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str, help='Token', required=True)

            args = parser.parse_args(strict=False)

            # Verify token.
            if 'token' in args:
                # Load participant from DB
                _request_ctx_stack.top.current_participant = TeraParticipant.get_participant_by_token(args['token'])

                if current_participant and current_participant.participant_enabled:
                    # Returns the function if authenticated with token
                    return f(*args, **kwargs)

                # Load device from DB
                _request_ctx_stack.top.current_device = TeraDevice.get_device_by_token(args['token'])

                if current_device and current_device.device_enabled:
                    # Returns the function if authenticated with token
                    return f(*args, **kwargs)

            # Any other case, do not call function
            return 'Forbidden', 403

        return decorated

    @staticmethod
    def certificate_required(f):
        """
        Use this decorator if UUID is stored in a client certificate.
        Acceptable for devices and participants.
        """
        @wraps(f)
        def decorated(*args, **kwargs):

            # Headers are modified in TwistedModule to add certificate information if available.
            # We are interested in the content of two fields : X-Device-Uuid, X-Participant-Uuid

            if request.headers.__contains__('X-Device-Uuid'):
                # Load device from DB
                _request_ctx_stack.top.current_device = TeraDevice.get_device_by_uuid(
                    request.headers['X-Device-Uuid'])
                if current_device and current_device.device_enabled:
                    return f(*args, **kwargs)

            elif request.headers.__contains__('X-Participant-Uuid'):
                # Load participant from DB
                _request_ctx_stack.top.current_participant = TeraParticipant.get_participant_by_uuid(
                    request.headers['X-Participant-Uuid'])
                if current_participant and current_participant.participant_enabled:
                    return f(*args, **kwargs)

            # Any other case, do not call function
            return 'Forbidden', 403

        return decorated

    @staticmethod
    def token_or_certificate_required(f):
        """
        Use this decorator if UUID is stored in a client certificate or token in url params.
        Acceptable for devices and participants.
        TODO - Avoid duplication of implementations from token_required, certificate_required.
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
                    return f(*args, **kwargs)

            elif request.headers.__contains__('X-Participant-Uuid'):
                # Load participant from DB
                _request_ctx_stack.top.current_participant = TeraParticipant.get_participant_by_uuid(
                    request.headers['X-Participant-Uuid'])

                if current_participant and current_participant.participant_enabled:
                    return f(*args, **kwargs)

            # Then verify tokens...

            # Parse args
            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str, help='Token', required=False)
            token_args = parser.parse_args(strict=False)

            # Verify token.
            if 'token' in token_args:
                # Load participant from DB
                _request_ctx_stack.top.current_participant = TeraParticipant.get_participant_by_token(token_args['token'])

                if current_participant and current_participant.participant_enabled:
                    # Returns the function if authenticated with token
                    return f(*args, **kwargs)

                # Load device from DB
                _request_ctx_stack.top.current_device = TeraDevice.get_device_by_token(token_args['token'])

                # Device must be found and enabled
                if current_device and current_device.device_enabled:
                    # Returns the function if authenticated with token
                    return f(*args, **kwargs)

            # Any other case, do not call function since no valid auth found.
            return 'Forbidden', 403

        return decorated

