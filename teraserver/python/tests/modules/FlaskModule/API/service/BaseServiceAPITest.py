import unittest
from modules.DatabaseModule.DBManager import DBManager
from modules.LoginModule.LoginModule import LoginModule
from opentera.config.ConfigManager import ConfigManager
from opentera.modules.BaseModule import BaseModule, ModuleNames
from flask.testing import FlaskClient
from opentera.redis.RedisVars import RedisVars
from opentera.db.models.TeraService import TeraService
from modules.FlaskModule.FlaskModule import FlaskModule, CustomAPI
import redis
import uuid
from flask import Flask
from flask_babel import Babel
import modules.Globals as Globals


class FakeFlaskModule(BaseModule):
    def __init__(self,  config: ConfigManager, flask_app=None):
        BaseModule.__init__(self, ModuleNames.FLASK_MODULE_NAME.value, config)
        self.flask_app = flask_app
        self.babel = Babel(self.flask_app)
        self.api = CustomAPI(self.flask_app, version='0.1', title='OpenTeraServer FakeAPI',
                             description='TeraServer API Documentation', prefix='/api')

        self.namespace = self.api.namespace('service', description='API for service calls')

        self.flask_app.debug = False
        self.flask_app.testing = True
        self.flask_app.secret_key = str(uuid.uuid4())
        self.flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        self.flask_app.config.update({'SESSION_REDIS': redis_url})
        self.flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        self.flask_app.config.update({'SESSION_COOKIE_SECURE': True})

        additional_args = {'test': True, 'flaskModule': self}
        FlaskModule.init_service_api(self, self.namespace, additional_args)


class BaseServiceAPITest(unittest.TestCase):

    test_endpoint = ''
    service_token = None
    service_uuid = None
    service_key = None

    @classmethod
    def setUpClass(cls):
        # Create Fake API
        cls._flask_app = Flask('FakeFlaskApp')
        cls._config = BaseServiceAPITest.getConfig()
        # This is needed for Logins and tokens
        cls._login_module = LoginModule(cls._config, cls._flask_app)
        Globals.login_module = cls._login_module  # TODO: Create a fake logger so we don't actually log?
        cls._db_man: DBManager = DBManager(cls._config, cls._flask_app)

        # Setup DB in RAM
        cls._db_man.open_local({}, echo=False, ram=True)

        with cls._flask_app.app_context():
            cls._flask_module = FakeFlaskModule(cls._config, cls._flask_app)
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
        self.setup_service_token()

    def tearDown(self):
        with self._flask_app.app_context():
            # Make sure pending queries are rollbacked.
            self._db_man.db.session.rollback()

    def setup_service_token(self):
        with self._flask_app.app_context():
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
