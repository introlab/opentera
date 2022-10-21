import unittest
from services.LoggingService.libloggingservice.db.Base import db
from services.LoggingService.libloggingservice.db.DBManager import DBManager
from services.LoggingService.ConfigManager import ConfigManager
from opentera.modules.BaseModule import BaseModule
from flask.testing import FlaskClient
from opentera.redis.RedisVars import RedisVars
from flask_session import Session
from services.LoggingService.FlaskModule import flask_app
import redis
import uuid
import random
from string import digits, ascii_lowercase, ascii_uppercase
import services.LoggingService.Globals as Globals
# from FakeLoggingService import FakeLoggingService


def infinite_jti_sequence():
    num = 0
    while True:
        yield num
        num += 1


# Initialize generator, call next(user_jti_generator) to get next sequence number
user_jti_generator = infinite_jti_sequence()


class FakeFlaskModule(BaseModule):
    def __init__(self,  config: ConfigManager):
        BaseModule.__init__(self, config.service_config['name'] + '.FlaskModule-test', config)

        flask_app.debug = False
        flask_app.test = True
        flask_app.secret_key = str(uuid.uuid4())  # Normally service UUID
        flask_app.config.update({'SESSION_TYPE': 'redis'})
        redis_url = redis.from_url('redis://%(username)s:%(password)s@%(hostname)s:%(port)s/%(db)s'
                                   % self.config.redis_config)

        flask_app.config.update({'SESSION_REDIS': redis_url})
        flask_app.config.update({'BABEL_DEFAULT_LOCALE': 'fr'})
        flask_app.config.update({'SESSION_COOKIE_SECURE': True})

        # Create session
        self.session = Session(flask_app)

        # Setup Fake Service API
        # from modules.FlaskModule.FlaskModule import service_api_ns


class BaseLoggingServiceAPITest(unittest.TestCase):

    test_endpoint = ''
    user_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for i in range(36))
    participant_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for i in range(36))
    service_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for i in range(36))
    device_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for i in range(36))

    @classmethod
    def setUpClass(cls):
        cls._config = BaseLoggingServiceAPITest.getConfig()
        cls._redis_client = redis.Redis(host=cls._config.redis_config['hostname'],
                                        port=cls._config.redis_config['port'],
                                        username=cls._config.redis_config['username'],
                                        password=cls._config.redis_config['password'],
                                        db=cls._config.redis_config['db'])

        cls._db_man: DBManager = DBManager(test=True)
        # Setup DB in RAM
        cls._db_man.open_local({}, echo=False, ram=True)

        # Creating default users / tests. Time-consuming, only once per test file.
        cls._db_man.create_defaults(cls._config, test=True)

        # Globals.service = FakeLoggingService()

    @classmethod
    def tearDownClass(cls):
        cls._config = None
        cls._db_man = None
        # LoginModule.redis_client = None
        db.session.remove()

    @classmethod
    def getConfig(cls) -> ConfigManager:
        config = ConfigManager()
        config.create_defaults()
        return config

    def setUp(self):
        self.setup_redis_keys()
        self.setup_service_access_manager()

    def tearDown(self):
        # Make sure pending queries are rollbacked.
        db.session.rollback()

    def setup_redis_keys(self):
        # Initialize keys (create only if not found)
        # Service (dynamic)
        if not self._redis_client.exists(RedisVars.RedisVar_ServiceTokenAPIKey):
            self._redis_client.set(RedisVars.RedisVar_ServiceTokenAPIKey, self.service_token_key)
        else:
            self.service_token_key = self._redis_client.get(RedisVars.RedisVar_ServiceTokenAPIKey).decode('utf-8')

        # User (dynamic)
        if not self._redis_client.exists(RedisVars.RedisVar_UserTokenAPIKey):
            self._redis_client.set(RedisVars.RedisVar_UserTokenAPIKey, self.user_token_key)
        else:
            self.user_token_key = self._redis_client.get(RedisVars.RedisVar_UserTokenAPIKey).decode('utf-8')

        # Participant (dynamic)
        if not self._redis_client.exists(RedisVars.RedisVar_ParticipantTokenAPIKey):
            self._redis_client.set(RedisVars.RedisVar_ParticipantTokenAPIKey, self.participant_token_key)
        else:
            self.participant_token_key = self._redis_client.get(
                RedisVars.RedisVar_ParticipantTokenAPIKey).decode('utf-8')

        # Device (dynamic)
        if not self._redis_client.exists(RedisVars.RedisVar_DeviceTokenAPIKey):
            self._redis_client.set(RedisVars.RedisVar_DeviceTokenAPIKey, self.device_token_key)

        # Device (static)
        if not self._redis_client.exists(RedisVars.RedisVar_DeviceStaticTokenAPIKey):
            self._redis_client.set(RedisVars.RedisVar_DeviceStaticTokenAPIKey, self.device_token_key)

        # Participant (static)
        if not self._redis_client.exists(RedisVars.RedisVar_ParticipantStaticTokenAPIKey):
            self._redis_client.set(RedisVars.RedisVar_ParticipantStaticTokenAPIKey, self.participant_token_key)

    def setup_service_access_manager(self):
        # Initialize service from redis, posing as LoggingService
        from opentera.services.ServiceAccessManager import ServiceAccessManager
        # Update Service Access information
        ServiceAccessManager.api_user_token_key = \
            self._redis_client.get(RedisVars.RedisVar_UserTokenAPIKey)
        ServiceAccessManager.api_participant_token_key = \
            self._redis_client.get(RedisVars.RedisVar_ParticipantTokenAPIKey)
        ServiceAccessManager.api_participant_static_token_key = \
            self._redis_client.get(RedisVars.RedisVar_ParticipantStaticTokenAPIKey)
        ServiceAccessManager.api_device_token_key = \
            self._redis_client.get(RedisVars.RedisVar_DeviceTokenAPIKey)
        ServiceAccessManager.api_device_static_token_key = \
            self._redis_client.get(RedisVars.RedisVar_DeviceStaticTokenAPIKey)
        ServiceAccessManager.api_service_token_key = \
            self._redis_client.get(RedisVars.RedisVar_ServiceTokenAPIKey)

        ServiceAccessManager.config_man = self._config

    def _generate_fake_user_token(self, name='FakeUser', superadmin=False, expiration=3600):

        import time
        import jwt
        import random
        import uuid

        # Creating token with user info
        now = time.time()
        token_key = self._redis_client.get(RedisVars.RedisVar_UserTokenAPIKey)

        payload = {
            'iat': int(now),
            'exp': int(now) + expiration,
            'iss': 'TeraServer',
            'jti': next(user_jti_generator),
            'user_uuid': str(uuid.uuid4()),
            'id_user': 1,
            'user_fullname': name,
            'user_superadmin': superadmin
        }

        return jwt.encode(payload, token_key, algorithm='HS256')

    def _get_with_service_token_auth(self, client: FlaskClient, token=None, params=None, endpoint=None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        if token is not None:
            headers = {'Authorization': 'OpenTera ' + token}
        else:
            headers = {}

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