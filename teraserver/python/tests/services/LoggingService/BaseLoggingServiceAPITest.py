import unittest
from services.LoggingService.libloggingservice.db.DBManager import DBManager
from services.LoggingService.ConfigManager import ConfigManager
from flask.testing import FlaskClient
import uuid
import random
from string import digits, ascii_lowercase, ascii_uppercase
import services.LoggingService.Globals as Globals
from FakeLoggingService import FakeLoggingService
from opentera.services.ServiceAccessManager import ServiceAccessManager


def infinite_jti_sequence():
    num = 0
    while True:
        yield num
        num += 1


# Initialize generator, call next(user_jti_generator) to get next sequence number
user_jti_generator = infinite_jti_sequence()


class BaseLoggingServiceAPITest(unittest.TestCase):
    _config = None
    _db_man = None
    test_endpoint = ''
    user_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for _ in range(36))
    participant_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for _ in range(36))
    service_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for _ in range(36))
    device_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for _ in range(36))

    @classmethod
    def setUpClass(cls):
        cls._config = BaseLoggingServiceAPITest.getConfig()

        # Instance of Fake service API will create a new flask_app
        Globals.service = FakeLoggingService()

        cls._db_man: DBManager = DBManager(app=Globals.service.flask_app, test=True)

        # Cheating using same db as FakeService
        cls._db_man.db = Globals.service.db_manager.db

        with BaseLoggingServiceAPITest.app_context():
            # Creating default users / tests. Time-consuming, only once per test file.
            cls._db_man.create_defaults(cls._config, test=True)

    @classmethod
    def app_context(cls):
        return Globals.service.flask_app.app_context()

    @classmethod
    def tearDownClass(cls):
        with BaseLoggingServiceAPITest.app_context():
            cls._db_man.db.session.remove()

    @classmethod
    def getConfig(cls) -> ConfigManager:
        config = ConfigManager()
        config.create_defaults()
        return config

    def setUp(self):
        self.test_client = Globals.service.flask_app.test_client()

    def tearDown(self):
        with BaseLoggingServiceAPITest.app_context():
            # Make sure pending queries are rollbacked.
            self._db_man.db.session.rollback()

    def _generate_fake_user_token(self, name='FakeUser', user_uuid=str(uuid.uuid4()),
                                  superadmin=False, expiration=3600):

        import time
        import jwt
        import random
        import uuid

        # Creating token with user info
        now = time.time()
        token_key = ServiceAccessManager.api_user_token_key

        payload = {
            'iat': int(now),
            'exp': int(now) + expiration,
            'iss': 'TeraServer',
            'jti': next(user_jti_generator),
            'user_uuid': user_uuid,
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

    def _post_with_service_token_auth(self, client: FlaskClient, token: str = '', json: dict = None,
                                      params: dict = None, endpoint: str = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.post(endpoint, headers=headers, query_string=params, json=json)

    def _delete_with_service_token_auth(self, client: FlaskClient, token: str = '',
                                        params: dict = None, endpoint: str = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.delete(endpoint, headers=headers, query_string=params)
