import unittest
from modules.DatabaseModule.DBManager import DBManager
from modules.LoginModule.LoginModule import LoginModule
from opentera.config.ConfigManager import ConfigManager
from opentera.modules.BaseModule import BaseModule, ModuleNames
from flask.testing import FlaskClient
from opentera.redis.RedisVars import RedisVars
from opentera.redis.RedisClient import RedisClient
from opentera.db.models.TeraService import TeraService


class FakeFlaskModule:
    def __init__(self,  config: ConfigManager):
        BaseModule.__init__(self, ModuleNames.FLASK_MODULE_NAME.value, config)


class BaseServiceAPITest(unittest.TestCase):

    test_endpoint = ''
    service_token = None
    service_uuid = None
    service_key = None

    @classmethod
    def setUpClass(cls):
        cls._config = BaseServiceAPITest.getConfig()
        cls._db_man = DBManager(cls._config)
        # Setup DB in RAM
        cls._db_man.open_local({}, echo=False, ram=True)

        # Creating default users / tests. Time-consuming, only once per test file.
        cls._db_man.create_defaults(cls._config, test=True)

        # This is needed for LoginModule to get key
        LoginModule.redis_client = RedisClient().redis

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def getConfig(cls) -> ConfigManager:
        config = ConfigManager()
        config.create_defaults()
        return config

    def setup_service_token(self):
        # Initialize service from redis, posing as VideoRehabService
        service: TeraService = TeraService.get_service_by_key('VideoRehabService')

        self.service_key = LoginModule.redis_client.get(RedisVars.RedisVar_ServiceTokenAPIKey).decode('utf-8')
        if not self.service_key:
            self.service_key = 'test_ServiceQueryDevices_key'
            LoginModule.redis_client.set(RedisVars.RedisVar_ServiceTokenAPIKey, self.service_key)

        self.service_token = service.get_token(self.service_key)
        self.service_uuid = service.service_uuid

    def _get_with_service_token_auth(self, client: FlaskClient, token, params=None, endpoint=None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.get(endpoint, headers=headers, query_string=params)
