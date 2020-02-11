
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

# Authentification schemes
http_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth("OpenTera")
multi_auth = MultiAuth(http_auth, token_auth)


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

        # Setup verify password function
        http_auth.verify_password(self.verify_password)
        token_auth.verify_token(self.verify_token)

    def load_user(self, user_id):
        print('LoginModule - load_user', user_id)
        return TeraUser.get_user_by_uuid(user_id)

    def verify_password(self, username, password):
        print('LoginModule - Verifying password for ', username)

        if TeraUser.verify_password(username=username, password=password):
            registered_user = TeraUser.get_user_by_username(username)
            print('Found user: ', registered_user)
            registered_user.update_last_online()

            login_user(registered_user, remember=True)
            print('Setting key with expiration in 60s', session['_id'], session['_user_id'])

            self.redisSet(session['_id'], session['_user_id'], ex=60)
            return True
        return False

    def verify_token(self, token_value):
        import jwt
        try:
            token_dict = jwt.decode(token_value, self.redisGet(TeraServerConstants.RedisVar_UserTokenAPIKey),
                                    algorithms='HS256')
        except jwt.exceptions.InvalidSignatureError as e:
            print(e)
            return False

        if token_dict['user_uuid']:
            registered_user = TeraUser.get_user_by_uuid(token_dict['user_uuid'])
            # TODO: Validate if user is also online?
            if registered_user is not None:
                registered_user.update_last_online()
                login_user(registered_user, remember=True)
                # TODO: Set user online in Redis??
                return True

        return False

    @staticmethod
    def token_required(f):
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
