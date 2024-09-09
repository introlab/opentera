from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser


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
            username = 'test'
            password = 'test'
            user = self.create_user_with_2fa_enabled(username, password)
            # Login with user
            response = self._get_with_user_http_auth(self.test_client, username, password)
            self.assertEqual(400, response.status_code)

    def create_user_with_2fa_enabled(self, username='test', password='test') -> TeraUser:
        # Create user with 2FA enabled
        user = TeraUser()
        user.user_firstname = 'Test'
        user.user_lastname = 'Test'
        user.user_email = 'test@hotmail.com'
        user.user_username = username
        user.user_password = password  # Password will be hashed in insert
        user.user_enabled = True
        user.user_profile = {}
        user.enable_2fa_otp()
        TeraUser.insert(user)
        return user


