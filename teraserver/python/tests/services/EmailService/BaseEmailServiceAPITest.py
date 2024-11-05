import unittest
from services.EmailService.libemailservice.db.DBManager import DBManager
from services.EmailService.ConfigManager import ConfigManager
from opentera.config.ConfigManager import ConfigManager as ConfigManagerServer
import services.EmailService.Globals as Globals
from services.EmailService.FlaskModule import flask_app
from flask.testing import FlaskClient
import uuid
import random
from string import digits, ascii_lowercase, ascii_uppercase
from tests.services.EmailService.FakeEmailService import FakeEmailService
from opentera.services.ServiceAccessManager import ServiceAccessManager
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraUser import TeraUser
from modules.LoginModule.LoginModule import LoginModule
from requests.auth import _basic_auth_str


def infinite_jti_sequence():
    num = 0
    while True:
        yield num
        num += 1


# Initialize generator, call next(user_jti_generator) to get next sequence number
user_jti_generator = infinite_jti_sequence()


class BaseEmailServiceAPITest(unittest.TestCase):
    _config = None
    _db_man = None
    test_endpoint = ''
    user_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for _ in range(36))
    participant_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for _ in range(36))
    service_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for _ in range(36))
    device_token_key = ''.join(random.choice(digits + ascii_lowercase + ascii_uppercase) for _ in range(36))
    user_login_endpoint = '/api/user/login'
    user_logout_endpoint = '/api/user/logout'

    @classmethod
    def setUpClass(cls):
        cls._config = BaseEmailServiceAPITest.getConfig()
        # Instance of Fake service API will create a new flask_app
        cls._service = FakeEmailService()

        # API Need those variables to be set
        Globals.service = cls._service
        flask_app.config.update({'UPLOAD_FOLDER': '.'})

        # Initialize DBManager with custom flask app
        cls._db_man: DBManager = DBManager(app=cls._service.flask_app, test=True)
        # Cheating using same db as FakeService
        cls._db_man.db = cls._service.db_manager.db

        # This is needed for Logins and tokens
        config_server = ConfigManagerServer()
        config_server.create_defaults()
        cls._login_module = LoginModule(config_server, cls._service.flask_app)

        with cls._service.flask_app.app_context():
            # Creating default users / tests. Time-consuming, only once per test file.
            cls._db_man.create_defaults(cls._config, test=True)

    def app_context(self):
        self.assertIsNotNone(self._service)
        self.assertIsNotNone(self._service.flask_app)
        return self._service.flask_app.app_context()

    @classmethod
    def tearDownClass(cls):
        with cls._service.flask_app.app_context():
            cls._db_man.db.session.remove()

    @classmethod
    def getConfig(cls) -> ConfigManager:
        config = ConfigManager()
        config.create_defaults()
        return config

    def setUp(self):
        self.assertIsNotNone(self._service)
        self.assertIsNotNone(self._service.flask_app)
        self.test_client = self._service.flask_app.test_client()
        self.assertIsNotNone(self.test_client)
        with self.app_context():
            service = TeraService.get_service_by_key('EmailService')
            Globals.service.service_info = service.to_json(minimal=False)

            user: TeraUser = TeraUser.get_user_by_username('admin')
            self.assertIsNotNone(user)
            self.assertIsNotNone(service)
            self.user_admin_token = user.get_token(ServiceAccessManager.api_user_token_key)
            self.assertIsNotNone(self.user_admin_token)
            self.assertGreater(len(self.user_admin_token), 0)

            user: TeraUser = TeraUser.get_user_by_username('user3')
            self.assertIsNotNone(user)
            self.user_user3_token = user.get_token(ServiceAccessManager.api_user_token_key)
            self.assertIsNotNone(self.user_user3_token)
            self.assertGreater(len(self.user_user3_token), 0)

            user: TeraUser = TeraUser.get_user_by_username('user4')
            self.assertIsNotNone(user)
            self.user_user4_token = user.get_token(ServiceAccessManager.api_user_token_key)
            self.assertIsNotNone(self.user_user4_token)
            self.assertGreater(len(self.user_user4_token), 0)

    def tearDown(self):
        with self.app_context():
            # Make sure pending queries are rollbacked.
            self._db_man.db.session.rollback()

    @staticmethod
    def _generate_fake_user_token(name='FakeUser', user_uuid=str(uuid.uuid4()), superadmin=False, expiration=3600):
        import time
        import jwt

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

    def _get_with_token_auth(self, client: FlaskClient, token=None, params=None, endpoint=None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        if token is not None:
            headers = {'Authorization': 'OpenTera ' + token}
        else:
            headers = {}

        return client.get(endpoint, headers=headers, query_string=params)

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

    def _post_with_token_auth(self, client: FlaskClient, token: str = '', json: dict = None,
                              params: dict = None, endpoint: str = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.post(endpoint, headers=headers, query_string=params, json=json,
                           content_type='application/json')

    def _post_file_with_token_auth(self, client: FlaskClient, token: str = '', files: dict = None,
                                   params: dict = None, endpoint: str = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}

        return client.post(endpoint, headers=headers, query_string=params, data=files,
                           content_type='multipart/form-data')

    def _delete_with_token_auth(self, client: FlaskClient, token: str = '',
                                params: dict = None, endpoint: str = None):
        if params is None:
            params = {}
        if endpoint is None:
            endpoint = self.test_endpoint
        headers = {'Authorization': 'OpenTera ' + token}
        return client.delete(endpoint, headers=headers, query_string=params)
