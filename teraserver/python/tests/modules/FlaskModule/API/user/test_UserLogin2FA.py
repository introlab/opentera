import pyotp
from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser


class UserLogin2FATest(BaseUserAPITest):
    test_endpoint = '/api/user/login_2fa'

    def setUp(self):
        super().setUp()
        # Create users with 2fa enabled
        with self._flask_app.app_context():
            self.user1: dict = self._create_2fa_enabled_user('test_user_2fa_1', 'password', set_secret=True)
            self.user2: dict = self._create_2fa_enabled_user('test_user_2fa_2', 'password', set_secret=False)

    def tearDown(self):
        # Delete users with 2fa enabled
        with self._flask_app.app_context():
            TeraUser.delete(self.user1['id_user'], hard_delete=True)
            TeraUser.delete(self.user2['id_user'], hard_delete=True)
        super().tearDown()


    def _create_2fa_enabled_user(self, username, password, set_secret:bool = True):
        user = TeraUser()
        user.id_user = 0 # New user
        user.user_username = username
        user.user_password = password
        user.user_firstname = username
        user.user_lastname = username
        user.user_email = f"{username}@test.com"
        user.user_enabled = True
        user.user_profile = {}
        if set_secret:
            user.enable_2fa_otp()
        else:
            user.user_2fa_enabled = True
            user.user_2fa_otp_enabled = False
            user.user_2fa_otp_secret = None

        TeraUser.insert(user)
        return user.to_json(minimal=False)


    def _login_user(self, username, password):
        response = self._get_with_user_http_auth(self.test_client, username, password, endpoint='/api/user/login')
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response.headers['Content-Type'])
        self.assertGreater(len(response.json), 0)
        return response

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, 'invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_no_session(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_admin_without_2fa_enabled(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('admin')
            self.assertIsNotNone(user)
            self.assertFalse(user.user_2fa_enabled)
            # Fist login
            response = self._login_user('admin', 'admin')
            self.assertEqual(200, response.status_code)

            # Now try to login with 2fa
            response = self._get_with_user_http_auth(self.test_client, 'admin', 'admin',
                                                     params={'otp_code': '123456'},
                                                     endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_login_user1_http_auth_no_code(self):
        with self._flask_app.app_context():

            # Fisrt login to create session
            response = self._login_user('test_user_2fa_1', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_validate_2fa' in response.json['redirect_url'])

            # Using default admin information, http auth not used
            response = self._get_with_user_http_auth(self.test_client)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_login_user1_http_auth_invalid_code(self):
        with self._flask_app.app_context():

            # First login to create session
            response = self._login_user('test_user_2fa_1', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_validate_2fa' in response.json['redirect_url'])

            # Then try to login with invalid code
            response = self._get_with_user_http_auth(self.test_client,
                                                     params={'otp_code': '123456'})
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_login_user1_http_auth_valid_code(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('test_user_2fa_1')
            self.assertIsNotNone(user.user_2fa_otp_secret)

            # First login to create session
            response = self._login_user('test_user_2fa_1', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_validate_2fa' in response.json['redirect_url'])
            self.assertFalse('login_setup_2fa' in response.json['redirect_url'])

            # Then try to login with valid code
            totp = pyotp.TOTP(user.user_2fa_otp_secret)
            response = self._get_with_user_http_auth(self.test_client,
                                                     params={'otp_code': totp.now()})
            self.assertEqual(200, response.status_code)
            self.assertTrue('user_uuid' in response.json)
            self.assertTrue('user_token' in response.json)
            self.assertFalse('websocket_url'in response.json)

    def test_get_endpoint_login_user1_http_auth_valid_code_with_websocket(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('test_user_2fa_1')
            self.assertIsNotNone(user.user_2fa_otp_secret)

            # First login to create session
            response = self._login_user('test_user_2fa_1', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_validate_2fa' in response.json['redirect_url'])
            self.assertFalse('login_setup_2fa' in response.json['redirect_url'])

            # Then try to login with valid code
            totp = pyotp.TOTP(user.user_2fa_otp_secret)
            response = self._get_with_user_http_auth(self.test_client,
                                                     params={'otp_code': totp.now(),
                                                             'with_websocket': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue('user_uuid' in response.json)
            self.assertTrue('user_token' in response.json)
            self.assertTrue('websocket_url'in response.json)

    def test_get_endpoint_login_user2_http_auth_invalid_code(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('test_user_2fa_2')
            self.assertIsNone(user.user_2fa_otp_secret)

            # First login to create session
            response = self._login_user('test_user_2fa_2', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertFalse('login_validate_2fa' in response.json['redirect_url'])
            self.assertTrue('login_setup_2fa' in response.json['redirect_url'])

            # Then try to login with invalid code
            response = self._get_with_user_http_auth(self.test_client,
                                                     params={'otp_code': '123456'})
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_login_user1_http_auth_valid_code_unknown_app_name(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('test_user_2fa_1')
            self.assertIsNotNone(user.user_2fa_otp_secret)

            # First login to create session
            response = self._login_user('test_user_2fa_1', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_validate_2fa' in response.json['redirect_url'])
            self.assertFalse('login_setup_2fa' in response.json['redirect_url'])

            # Then try to login with valid code
            totp = pyotp.TOTP(user.user_2fa_otp_secret)
            response = self._get_with_user_http_auth(self.test_client,
                                                     params={'otp_code': totp.now()},
                                                     opt_headers={'X-Client-Name': 'test', 'X-Client-Version': '0.0.0'})
            self.assertEqual(200, response.status_code)
            self.assertTrue('user_uuid' in response.json)
            self.assertTrue('user_token' in response.json)
            self.assertFalse('websocket_url'in response.json)

    def test_get_endpoint_login_user1_http_auth_valid_code_outdated_app(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('test_user_2fa_1')
            self.assertIsNotNone(user.user_2fa_otp_secret)

            # First login to create session
            response = self._login_user('test_user_2fa_1', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_validate_2fa' in response.json['redirect_url'])
            self.assertFalse('login_setup_2fa' in response.json['redirect_url'])

            # Then try to login with valid code
            totp = pyotp.TOTP(user.user_2fa_otp_secret)
            response = self._get_with_user_http_auth(self.test_client,
                                                     params={'otp_code': totp.now()},
                                                     opt_headers={'X-Client-Name': 'OpenTeraPlus',
                                                                  'X-Client-Version': '0.0.0'})
            self.assertEqual(426, response.status_code)

    def test_get_endpoint_login_user1_http_auth_valid_code_valid_app(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('test_user_2fa_1')
            self.assertIsNotNone(user.user_2fa_otp_secret)

            # First login to create session
            response = self._login_user('test_user_2fa_1', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_validate_2fa' in response.json['redirect_url'])
            self.assertFalse('login_setup_2fa' in response.json['redirect_url'])

            # Then try to login with valid code
            totp = pyotp.TOTP(user.user_2fa_otp_secret)
            response = self._get_with_user_http_auth(self.test_client,
                                                     params={'otp_code': totp.now()},
                                                     opt_headers={'X-Client-Name': 'OpenTeraPlus',
                                                                  'X-Client-Version': '1.0.0'})
            self.assertEqual(200, response.status_code)
