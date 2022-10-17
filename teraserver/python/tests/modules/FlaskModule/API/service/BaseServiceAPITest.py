import unittest
from opentera.db.Base import db
from modules.DatabaseModule.DBManager import DBManager
from modules.LoginModule.LoginModule import LoginModule
from opentera.config.ConfigManager import ConfigManager
from opentera.modules.BaseModule import BaseModule, ModuleNames
from flask.testing import FlaskClient
from opentera.redis.RedisVars import RedisVars
from opentera.redis.RedisClient import RedisClient
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServerSettings import TeraServerSettings
from flask_session import Session
from modules.FlaskModule.FlaskModule import flask_app
import redis


class FakeFlaskModule(BaseModule):
    def __init__(self,  config: ConfigManager):
        BaseModule.__init__(self, ModuleNames.FLASK_MODULE_NAME.value, config)

        flask_app.debug = False
        flask_app.test = True
        flask_app.secret_key = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerUUID)
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        flask_app.config.update({'SESSION_COOKIE_SECURE': True})

        # Create session
        self.session = Session(flask_app)


class BaseServiceAPITest(unittest.TestCase):

    test_endpoint = ''
    service_token = None
    service_uuid = None
    service_key = None

    @classmethod
    def setUpClass(cls):
        cls._config = BaseServiceAPITest.getConfig()
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

    def setUp(self):
        self.setup_service_token()

    def tearDown(self):
        # Make sure pending queries are rollbacked.
        db.session.rollback()

    def setup_service_token(self):
        # Initialize service from redis, posing as VideoRehabService
        service: TeraService = TeraService.get_service_by_key('VideoRehabService')

        self.assertIsNotNone(service)
        self.assertIsNotNone(LoginModule.redis_client)

        if not LoginModule.redis_client.exists(RedisVars.RedisVar_ServiceTokenAPIKey):
            self.service_key = 'BaseServiceAPITest'
            LoginModule.redis_client.set(RedisVars.RedisVar_ServiceTokenAPIKey, self.service_key)
        else:
            self.service_key = LoginModule.redis_client.get(RedisVars.RedisVar_ServiceTokenAPIKey).decode('utf-8')

        self.assertIsNotNone(self.service_key)
        self.service_token = service.get_token(self.service_key)
        self.service_uuid = service.service_uuid
        self.id_service = service.id_service

    def _get_with_service_token_auth(self, client: FlaskClient, token, params={}, endpoint=None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.get(endpoint, headers=headers, query_string=params)

    def _post_with_service_token_auth(self, client: FlaskClient, token: str = '', json: dict = {},
                                      params: dict = {}, endpoint: str = ''):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.post(endpoint, headers=headers, query_string=params, json=json)

    def _delete_with_service_token_auth(self, client: FlaskClient, token: str = '',
                                        params: dict = {}, endpoint: str = ''):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.delete(endpoint, headers=headers, query_string=params)
