from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser
import pyotp


class UserLogin2FATest(BaseUserAPITest):
    test_endpoint = '/api/user/login_2fa'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, 'invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_login_admin_user_http_auth_no_code(self):
        with self._flask_app.app_context():
            # Using default admin information
            response = self._get_with_user_http_auth(self.test_client, 'admin', 'admin')
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_login_admin_user_http_auth_invalid_code(self):
        with self._flask_app.app_context():
            # Using default admin information
            # Admin account has no 2FA enabled by default
            params = {'otp_code': 'invalid'}
            response = self._get_with_user_http_auth(self.test_client, 'admin', 'admin',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_login_2fa_enabled_user_no_code(self):
        with self._flask_app.app_context():
            # Create user with 2FA enabled
            username = f'test_{pyotp.random_base32(32)}'
            password = pyotp.random_base32(32)
            user = self.create_user_with_2fa_enabled(username, password)
            self.assertIsNotNone(user.user_2fa_otp_secret)
            self.assertTrue(user.user_2fa_enabled)
            self.assertTrue(user.user_2fa_otp_enabled)
            # Login with user
            response = self._get_with_user_http_auth(self.test_client, username, password)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_login_2fa_enabled_user_wrong_code(self):
        with self._flask_app.app_context():
            # Create user with 2FA enabled
            username = f'test_{pyotp.random_base32(32)}'
            password = pyotp.random_base32(32)
            user = self.create_user_with_2fa_enabled(username, password)
            self.assertIsNotNone(user.user_2fa_otp_secret)
            self.assertTrue(user.user_2fa_enabled)
            self.assertTrue(user.user_2fa_otp_enabled)
            # Login with user
            params = {'otp_code': 'invalid'}
            response = self._get_with_user_http_auth(self.test_client, username, password, params=params)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_login_2fa_enabled_user_valid_code(self):
        with self._flask_app.app_context():
            # Create user with 2FA enabled
            username = f'test_{pyotp.random_base32(32)}'
            password = pyotp.random_base32(32)
            user = self.create_user_with_2fa_enabled(username, password)
            self.assertIsNotNone(user.user_2fa_otp_secret)
            self.assertTrue(user.user_2fa_enabled)
            self.assertTrue(user.user_2fa_otp_enabled)
            # Login with user
            totp = pyotp.TOTP(user.user_2fa_otp_secret)
            params = {'otp_code': totp.now()}
            response = self._get_with_user_http_auth(self.test_client, username, password, params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertGreater(len(response.json), 0)
            self.assertTrue('user_uuid' in response.json)
            self.assertTrue('user_token' in response.json)

    def test_get_endpoint_login_2fa_enabled_user_valid_code_with_websockets(self):
        with self._flask_app.app_context():
            # Create user with 2FA enabled
            username = f'test_{pyotp.random_base32(32)}'
            password = pyotp.random_base32(32)
            user = self.create_user_with_2fa_enabled(username, password)
            self.assertIsNotNone(user.user_2fa_otp_secret)
            self.assertTrue(user.user_2fa_enabled)
            self.assertTrue(user.user_2fa_otp_enabled)
            # Login with user
            totp = pyotp.TOTP(user.user_2fa_otp_secret)
            params = {'otp_code': totp.now(), 'with_websocket': True}
            response = self._get_with_user_http_auth(self.test_client, username, password, params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertGreater(len(response.json), 0)
            self.assertTrue('user_uuid' in response.json)
            self.assertTrue('user_token' in response.json)
            self.assertTrue('websocket_url' in response.json)
            self.assertIsNotNone(response.json['websocket_url'])

    def test_get_endpoint_login_2fa_enabled_user_unknown_app_name_and_version(self):
        with self._flask_app.app_context():
            # Create user with 2FA enabled
            username = f'test_{pyotp.random_base32(32)}'
            password = pyotp.random_base32(32)
            user = self.create_user_with_2fa_enabled(username, password)
            self.assertIsNotNone(user.user_2fa_otp_secret)
            self.assertTrue(user.user_2fa_enabled)
            self.assertTrue(user.user_2fa_otp_enabled)
            # Login with user
            totp = pyotp.TOTP(user.user_2fa_otp_secret)
            params = {'otp_code': totp.now(), 'with_websocket': True}
            response = self._get_with_user_http_auth(self.test_client, username, password, params=params,
                                                     opt_headers={'X-Client-Name': 'test', 'X-Client-Version': '0.0.0'})
            self.assertEqual(200, response.status_code)

    def test_get_endpoint_login_2fa_enabled_user_outdated_app_version(self):
        with self._flask_app.app_context():
            # Create user with 2FA enabled
            username = f'test_{pyotp.random_base32(32)}'
            password = pyotp.random_base32(32)
            user = self.create_user_with_2fa_enabled(username, password)
            self.assertIsNotNone(user.user_2fa_otp_secret)
            self.assertTrue(user.user_2fa_enabled)
            self.assertTrue(user.user_2fa_otp_enabled)
            # Login with user
            totp = pyotp.TOTP(user.user_2fa_otp_secret)
            params = {'otp_code': totp.now(), 'with_websocket': True}
            response = self._get_with_user_http_auth(self.test_client, username, password, params=params,
                                                     opt_headers={'X-Client-Name': 'OpenTeraPlus',
                                                                  'X-Client-Version': '0.0.0'})
            self.assertTrue('version_latest' in response.json)
            self.assertTrue('version_error' in response.json)
            self.assertEqual(426, response.status_code)

    def test_get_endpoint_login_2fa_enabled_user_valid_app_version(self):
        with self._flask_app.app_context():
            # Create user with 2FA enabled
            username = f'test_{pyotp.random_base32(32)}'
            password = pyotp.random_base32(32)
            user = self.create_user_with_2fa_enabled(username, password)
            self.assertIsNotNone(user.user_2fa_otp_secret)
            self.assertTrue(user.user_2fa_enabled)
            self.assertTrue(user.user_2fa_otp_enabled)
            # Login with user
            totp = pyotp.TOTP(user.user_2fa_otp_secret)
            params = {'otp_code': totp.now(), 'with_websocket': True}
            response = self._get_with_user_http_auth(self.test_client, username, password, params=params,
                                                     opt_headers={'X-Client-Name': 'OpenTeraPlus',
                                                                  'X-Client-Version': '1.0.0'})
            self.assertTrue('version_latest' in response.json)
            self.assertFalse('version_error' in response.json)
            self.assertEqual(200, response.status_code)

    def create_user_with_2fa_enabled(self, username='test', password='test') -> TeraUser:
        # Create user with 2FA enabled
        user = TeraUser()
        user.user_firstname = 'Test'
        user.user_lastname = 'Test'
        user.user_email = f'{username}@hotmail.com'
        user.user_username = username
        user.user_password = password  # Password will be hashed in insert
        user.user_enabled = True
        user.user_profile = {}
        user.enable_2fa_otp()
        TeraUser.insert(user)
        return user
