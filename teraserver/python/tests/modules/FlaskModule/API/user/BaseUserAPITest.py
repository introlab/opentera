import unittest
from opentera.db.Base import db
from modules.DatabaseModule.DBManager import DBManager
from modules.LoginModule.LoginModule import LoginModule
from opentera.config.ConfigManager import ConfigManager
from opentera.modules.BaseModule import BaseModule, ModuleNames
from flask.testing import FlaskClient
from opentera.redis.RedisVars import RedisVars
from opentera.db.models.TeraServerSettings import TeraServerSettings
from flask_session import Session
from modules.FlaskModule.FlaskModule import flask_app
import redis
from requests.auth import _basic_auth_str


class FakeFlaskModule(BaseModule):
    def __init__(self,  config: ConfigManager):
        BaseModule.__init__(self, ModuleNames.FLASK_MODULE_NAME.value, config)

        flask_app.debug = False
        flask_app.testing = True
        flask_app.secret_key = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerUUID)
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        flask_app.config.update({'SESSION_COOKIE_SECURE': True})

        # Create session
        self.session = Session(flask_app)


class BaseUserAPITest(unittest.TestCase):
    test_endpoint: str = ''
    user_token_key = TeraServerSettings.generate_token_key(32)
    participant_token_key = TeraServerSettings.generate_token_key(32)
    service_token_key = TeraServerSettings.generate_token_key(32)

    @classmethod
    def setUpClass(cls):
        cls._config = BaseUserAPITest.getConfig()
        cls._db_man: DBManager = DBManager(cls._config)
        # Setup DB in RAM
        cls._db_man.open_local({}, echo=False, ram=True)

        # Creating default users / tests. Time-consuming, only once per test file.
        cls._db_man.create_defaults(cls._config, test=True)

        # This is needed for Logins and tokens
        cls._login_module = LoginModule(cls._config)

    @classmethod
    def tearDownClass(cls):
        cls._config = None
        cls._db_man = None
        LoginModule.redis_client = None
        db.session.remove()

    @classmethod
    def getConfig(cls) -> ConfigManager:
        config = ConfigManager()
        config.create_defaults()
        return config

    @classmethod
    def reset_database(cls):
        # db.close()
        # Create all tables
        config = cls.getConfig()
        manager = DBManager(config)
        manager.open_local({}, echo=False, ram=True)

        # Creating default users / tests. Time-consuming, only once per test file.
        manager.create_defaults(config, test=True)

    def setUp(self):
        # Setup required keys
        self.setup_redis_keys()
        self.session = db.create_scoped_session()

    def tearDown(self):
        # Make sure pending queries are rollbacked.
        self.session.remove()

    def setup_redis_keys(self):
        # Initialize keys (create only if not found)
        # Service (dynamic)
        if not LoginModule.redis_client.exists(RedisVars.RedisVar_ServiceTokenAPIKey):
            LoginModule.redis_client.set(RedisVars.RedisVar_ServiceTokenAPIKey, self.service_token_key)
        else:
            self.service_token_key = LoginModule.redis_client.get(RedisVars.RedisVar_ServiceTokenAPIKey).decode('utf-8')

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

    def _get_with_user_token_auth(self, client: FlaskClient, token: str = '', params=None, endpoint=None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.get(endpoint, headers=headers, query_string=params)

    def _get_with_user_http_auth(self, client: FlaskClient, username: str = '', password: str = '',
                                 params=None, endpoint=None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint

        headers = {'Authorization': _basic_auth_str(username, password)}
        return client.get(endpoint, headers=headers, query_string=params)

    def _post_with_user_token_auth(self, client: FlaskClient, token: str = '', json: dict = {},
                                   params: dict = None, endpoint: str = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.post(endpoint, headers=headers, query_string=params, json=json)

    def _post_with_user_http_auth(self, client: FlaskClient, username: str = '', password: str = '',
                                  json: dict = {}, params: dict = None, endpoint: str = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': _basic_auth_str(username, password)}
        return client.post(endpoint, headers=headers, query_string=params, json=json)

    def _delete_with_user_token_auth(self, client: FlaskClient, token: str = '',
                                     params: dict = None, endpoint: str = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.delete(endpoint, headers=headers, query_string=params)

    def _delete_with_user_http_auth(self, client: FlaskClient, username: str = '', password: str = '',
                                    params: dict = None, endpoint: str = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': _basic_auth_str(username, password)}
        return client.delete(endpoint, headers=headers, query_string=params)
