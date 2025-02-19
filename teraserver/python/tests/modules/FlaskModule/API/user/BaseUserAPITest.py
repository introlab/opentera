import unittest
from modules.DatabaseModule.DBManager import DBManager
from modules.LoginModule.LoginModule import LoginModule
from opentera.config.ConfigManager import ConfigManager
from opentera.modules.BaseModule import BaseModule, ModuleNames
from flask.testing import FlaskClient
from opentera.redis.RedisVars import RedisVars
from opentera.db.models.TeraServerSettings import TeraServerSettings
from modules.UserManagerModule.UserManagerModule import UserManagerModule
from requests.auth import _basic_auth_str
import modules.Globals as Globals
from modules.FlaskModule.FlaskModule import FlaskModule, CustomAPI
import redis
import uuid
from flask_babel import Babel
from flask import Flask
from opentera.modules.BaseModule import ModuleNames


class FakeFlaskModule(BaseModule):
    def __init__(self, config: ConfigManager, flask_app=None, user_manager_module=None):
        BaseModule.__init__(self, ModuleNames.FLASK_MODULE_NAME.value, config)
        self.flask_app = flask_app
        self.babel = Babel(self.flask_app)
        self.api = CustomAPI(self.flask_app, version='0.1', title='OpenTeraServer FakeAPI',
                             description='TeraServer API Documentation', prefix='/api')

        self.namespace = self.api.namespace('user', description='API for user calls')

        self.flask_app.debug = False
        self.flask_app.testing = True
        self.flask_app.secret_key = str(uuid.uuid4())
        self.flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        self.flask_app.config.update({'SESSION_REDIS': redis_url})
        self.flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        self.flask_app.config.update({'SESSION_COOKIE_SECURE': True})
        self.flask_app.config.update({'PROPAGATE_EXCEPTIONS': True})

        additional_args = {'test': True,
                           'user_manager_module': user_manager_module,
                           'flaskModule': self}

        FlaskModule.init_user_api(self, self.namespace, additional_args)

    def send_user_disconnect_module_message(self, user_uuid: str):
        print('FakeFlaskModule : send_user_disconnect_module_message')
        pass

    def send_participant_disconnect_module_message(self, participant_uuid: str):
        print('FakeFlaskModule : send_participant_disconnect_module_message')
        pass

    def send_device_disconnect_module_message(self, device_uuid: str):
        print('FakeFlaskModule : send_device_disconnect_module_message')
        pass


class BaseUserAPITest(unittest.TestCase):
    test_endpoint: str = ''
    user_token_key = TeraServerSettings.generate_token_key(32)
    participant_token_key = TeraServerSettings.generate_token_key(32)
    service_token_key = TeraServerSettings.generate_token_key(32)

    @classmethod
    def setUpClass(cls):
        from modules.FlaskModule.FlaskModule import flask_app
        flask_app.testing = True

        # Create Fake API
        cls._flask_app = Flask('FakeFlaskApp')
        cls._config = BaseUserAPITest.getConfig()
        # This is needed for Logins and tokens
        cls._login_module = LoginModule(cls._config, cls._flask_app)

        # This is needed for User management
        cls._user_manager_module = UserManagerModule(cls._config)

        Globals.login_module = cls._login_module  # TODO: Create a fake logger so we don't actually log?
        cls._db_man: DBManager = DBManager(cls._config, cls._flask_app)

        # Setup DB in RAM
        cls._db_man.open_local({}, echo=False, ram=True)

        with cls._flask_app.app_context():
            cls._flask_module = FakeFlaskModule(cls._config, cls._flask_app, cls._user_manager_module)
            # Creating default users / tests. Time-consuming, only once per test file.
            cls._db_man.create_defaults(cls._config, test=True)

    @classmethod
    def tearDownClass(cls):
        with cls._flask_app.app_context():
            cls._config = None
            cls._db_man.db.session.remove()
            cls._db_man = None
            LoginModule.redis_client = None

    @classmethod
    def getConfig(cls) -> ConfigManager:
        config = ConfigManager()
        config.create_defaults()
        return config

    def setUp(self):
        self.test_client = self._flask_module.flask_app.test_client()
        # Setup required keys
        self.setup_redis_keys()

    def tearDown(self):
        with self._flask_app.app_context():
            # Make sure pending queries are rollbacked.
            self._db_man.db.session.rollback()

    def setup_redis_keys(self):
        # Initialize keys (create only if not found)
        # Service (dynamic)
        with self._flask_app.app_context():
            if not LoginModule.redis_client.exists(RedisVars.RedisVar_ServiceTokenAPIKey):
                LoginModule.redis_client.set(RedisVars.RedisVar_ServiceTokenAPIKey, self.service_token_key)
            else:
                self.service_token_key = LoginModule.redis_client.get(RedisVars.RedisVar_ServiceTokenAPIKey)\
                    .decode('utf-8')

            # User (dynamic)
            if not LoginModule.redis_client.exists(RedisVars.RedisVar_UserTokenAPIKey):
                LoginModule.redis_client.set(RedisVars.RedisVar_UserTokenAPIKey, self.user_token_key)
            else:
                self.user_token_key = LoginModule.redis_client.get(RedisVars.RedisVar_UserTokenAPIKey).decode('utf-8')

            # Participant (dynamic)
            if not LoginModule.redis_client.exists(RedisVars.RedisVar_ParticipantTokenAPIKey):
                LoginModule.redis_client.set(RedisVars.RedisVar_ParticipantTokenAPIKey, self.participant_token_key)
            else:
                self.participant_token_key = LoginModule.redis_client.get(
                    RedisVars.RedisVar_ParticipantTokenAPIKey).decode('utf-8')

            if not LoginModule.redis_client.exists(RedisVars.RedisVar_DeviceTokenAPIKey):
                LoginModule.redis_client.set(RedisVars.RedisVar_DeviceTokenAPIKey,
                                             TeraServerSettings.get_server_setting_value(
                                                 TeraServerSettings.ServerDeviceTokenKey))

            if not LoginModule.redis_client.exists(RedisVars.RedisVar_DeviceStaticTokenAPIKey):
                LoginModule.redis_client.set(RedisVars.RedisVar_DeviceStaticTokenAPIKey,
                                             TeraServerSettings.get_server_setting_value(
                                                 TeraServerSettings.ServerDeviceTokenKey))

            if not LoginModule.redis_client.exists(RedisVars.RedisVar_ParticipantStaticTokenAPIKey):
                LoginModule.redis_client.set(RedisVars.RedisVar_ParticipantStaticTokenAPIKey,
                                             TeraServerSettings.get_server_setting_value(
                                                 TeraServerSettings.ServerParticipantTokenKey))

    def _get_with_user_token_auth(self, client: FlaskClient, token: str = '', params=None, endpoint=None,
                                  opt_headers: dict = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        if opt_headers is not None:
            headers.update(opt_headers)

        return client.get(endpoint, headers=headers, query_string=params)

    def _get_with_user_http_auth(self, client: FlaskClient, username: str = '', password: str = '',
                                 params: dict = None, endpoint: str = None, opt_headers: dict = None):
        if params is None:
             params = {}
        if endpoint is None:
            endpoint = self.test_endpoint

        headers = {'Authorization': _basic_auth_str(username, password)}
        if opt_headers is not None:
            headers.update(opt_headers)

        return client.get(endpoint, headers=headers, query_string=params)

    def _post_with_user_token_auth(self, client: FlaskClient, token: str = '', json: dict = {},
                                   params: dict = None, endpoint: str = None, opt_headers: dict = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}

        if opt_headers is not None:
            headers.update(opt_headers)

        return client.post(endpoint, headers=headers, query_string=params, json=json)

    def _post_with_user_http_auth(self, client: FlaskClient, username: str = '', password: str = '',
                                  json: dict = {}, params: dict = None, endpoint: str = None, opt_headers: dict = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': _basic_auth_str(username, password)}
        if opt_headers is not None:
            headers.update(opt_headers)
        return client.post(endpoint, headers=headers, query_string=params, json=json)

    def _post_file_with_user_http_auth(self, client: FlaskClient, files: dict, username: str = '', password: str = '',
                                       params: dict = None, endpoint: str = None, opt_headers: dict = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': _basic_auth_str(username, password)}

        if opt_headers is not None:
            headers.update(opt_headers)

        return client.post(endpoint, headers=headers, query_string=params, data=files)

    def _delete_with_user_token_auth(self, client: FlaskClient, token: str = '',
                                     params: dict = None, endpoint: str = None, opt_headers: dict = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}

        if opt_headers is not None:
            headers.update(opt_headers)

        return client.delete(endpoint, headers=headers, query_string=params)

    def _delete_with_user_http_auth(self, client: FlaskClient, username: str = '', password: str = '',
                                    params: dict = None, endpoint: str = None, opt_headers: dict = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': _basic_auth_str(username, password)}

        if opt_headers is not None:
            headers.update(opt_headers)

        return client.delete(endpoint, headers=headers, query_string=params)
