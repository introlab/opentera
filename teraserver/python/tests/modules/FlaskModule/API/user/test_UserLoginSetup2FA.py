import pyotp
from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser


class UserLoginSetup2FATest(BaseUserAPITest):
    test_endpoint = '/api/user/login_setup_2fa'

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
        response = self._get_with_user_http_auth(self.test_client, username,
                                                 password, endpoint='/api/user/login')
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response.headers['Content-Type'])
        self.assertGreater(len(response.json), 0)
        return response

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

            # Now try to setup 2fa
            response = self._get_with_user_http_auth(self.test_client, 'admin', 'admin',
                                                     endpoint=self.test_endpoint)

            self.assertEqual(403, response.status_code)

    def test_get_endpoint_login_user1_2fa_already_setup(self):
        with self._flask_app.app_context():

            # Fisrt login to create session
            response = self._login_user('test_user_2fa_1', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertFalse('login_setup_2fa' in response.json['redirect_url'])

            # Using default admin information, http auth not used
            response = self._get_with_user_http_auth(self.test_client)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_login_user2_http_auth_should_work_but_and_modify_user_after_post(self):
        with self._flask_app.app_context():

            # First login to create session
            response = self._login_user('test_user_2fa_2', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_setup_2fa' in response.json['redirect_url'])

            # Then try to setup 2fa
            response = self._get_with_user_http_auth(self.test_client)
            self.assertEqual(200, response.status_code)

            self.assertTrue('qr_code' in response.json)
            self.assertTrue('otp_secret' in response.json)

            user = TeraUser.get_user_by_username('test_user_2fa_2')
            self.assertIsNotNone(user)
            self.assertTrue(user.user_2fa_enabled)
            self.assertFalse(user.user_2fa_otp_enabled)
            self.assertIsNone(user.user_2fa_otp_secret)

            # Post will enable 2fa
            otp_secret = response.json['otp_secret']
            otp_code = pyotp.TOTP(response.json['otp_secret']).now()
            params = {'otp_secret': response.json['otp_secret'], 'otp_code': otp_code}
            response = self.test_client.post(self.test_endpoint, json=params)
            self.assertEqual(200, response.status_code)

            # Verify response
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_validate_2fa' in response.json['redirect_url'])

            # Reload user and verify 2fa is enabled properly
            user = TeraUser.get_user_by_username('test_user_2fa_2')
            self.assertIsNotNone(user)
            self.assertTrue(user.user_2fa_enabled)
            self.assertTrue(user.user_2fa_otp_enabled)
            self.assertIsNotNone(user.user_2fa_otp_secret)
            self.assertEqual(otp_secret, user.user_2fa_otp_secret)

    def test_get_endpoint_login_user2_http_auth_should_fail_after_post_with_wrong_code(self):
        with self._flask_app.app_context():

            # First login to create session
            response = self._login_user('test_user_2fa_2', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_setup_2fa' in response.json['redirect_url'])

            # Then try to setup 2fa
            response = self._get_with_user_http_auth(self.test_client)
            self.assertEqual(200, response.status_code)

            self.assertTrue('qr_code' in response.json)
            self.assertTrue('otp_secret' in response.json)

            user = TeraUser.get_user_by_username('test_user_2fa_2')
            self.assertIsNotNone(user)
            self.assertTrue(user.user_2fa_enabled)
            self.assertFalse(user.user_2fa_otp_enabled)
            self.assertIsNone(user.user_2fa_otp_secret)

            # Post will fail with wrong code
            params = {'otp_secret': response.json['otp_secret'], 'otp_code': '123456'}
            response = self.test_client.post(self.test_endpoint, json=params)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_login_user2_http_auth_should_fail_after_post_with_wrong_secret(self):
        with self._flask_app.app_context():

            # First login to create session
            response = self._login_user('test_user_2fa_2', 'password')
            self.assertEqual(200, response.status_code)
            self.assertTrue('redirect_url' in response.json)
            self.assertTrue('login_setup_2fa' in response.json['redirect_url'])

            # Then try to setup 2fa
            response = self._get_with_user_http_auth(self.test_client)
            self.assertEqual(200, response.status_code)

            self.assertTrue('qr_code' in response.json)
            self.assertTrue('otp_secret' in response.json)

            user = TeraUser.get_user_by_username('test_user_2fa_2')
            self.assertIsNotNone(user)
            self.assertTrue(user.user_2fa_enabled)
            self.assertFalse(user.user_2fa_otp_enabled)
            self.assertIsNone(user.user_2fa_otp_secret)

            # Post will fail with wrong secret
            otp_secret = pyotp.random_base32()
            otp_code = pyotp.TOTP(otp_secret).now()
            params = {'otp_secret': response.json['otp_secret'], 'otp_code': otp_code}
            response = self.test_client.post(self.test_endpoint, json=params)
            self.assertEqual(401, response.status_code)
