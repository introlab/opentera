from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser


class UserLogoutTest(BaseUserAPITest):

    test_endpoint = '/api/user/logout'
    login_endpoint = '/api/user/login'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_logout_valid_admin_httpauth(self):
        with self._flask_app.app_context():
            # Using default admin information
            username = 'admin'
            password = 'admin'

            login_response = self._get_with_user_http_auth(
                self.test_client, username, password, params={}, endpoint=self.login_endpoint)

            self.assertEqual(200, login_response.status_code)
            self.assertEqual('application/json', login_response.headers['Content-Type'])
            self.assertGreater(len(login_response.json), 0)

            logout_response = self._get_with_user_http_auth(
                self.test_client, username, password, params={}, endpoint=self.test_endpoint)

            self.assertEqual('application/json', logout_response.headers['Content-Type'])
            self.assertEqual(200, logout_response.status_code)

    def test_logout_invalid_user_httpauth(self):
        with self._flask_app.app_context():
            username = 'invalid'
            password = 'invalid'

            login_response = self._get_with_user_http_auth(
                self.test_client, username, password, params={}, endpoint=self.login_endpoint)

            self.assertEqual(401, login_response.status_code)

            logout_response = self._get_with_user_http_auth(
                self.test_client, username, password, params={}, endpoint=self.test_endpoint)

            self.assertEqual(401, logout_response.status_code)

    def test_logout_valid_token_auth(self):
        with self._flask_app.app_context():
            # Using default admin information
            username = 'admin'
            password = 'admin'

            login_response = self._get_with_user_http_auth(
                self.test_client, username, password, params={}, endpoint=self.login_endpoint)

            self.assertEqual(200, login_response.status_code)
            self.assertEqual('application/json', login_response.headers['Content-Type'])
            self.assertGreater(len(login_response.json), 0)
            self.assertTrue('user_token' in login_response.json)

            token = login_response.json['user_token']

            logout_response = self._get_with_user_token_auth(
                self.test_client, token, params={}, endpoint=self.test_endpoint)

            self.assertEqual('application/json', logout_response.headers['Content-Type'])
            self.assertEqual(200, logout_response.status_code)

    def test_logout_twice_should_not_be_authorized_because_of_disabled_token(self):
        with self._flask_app.app_context():
            # Using default admin information
            username = 'admin'
            password = 'admin'

            login_response = self._get_with_user_http_auth(
                self.test_client, username, password, params={}, endpoint=self.login_endpoint)

            self.assertEqual(200, login_response.status_code)
            self.assertEqual('application/json', login_response.headers['Content-Type'])
            self.assertGreater(len(login_response.json), 0)
            self.assertTrue('user_token' in login_response.json)

            token = login_response.json['user_token']

            # First logout should work
            logout_response = self._get_with_user_token_auth(
                self.test_client, token, params={}, endpoint=self.test_endpoint)

            self.assertEqual('application/json', logout_response.headers['Content-Type'])
            self.assertEqual(200, logout_response.status_code)

            # Second logout should not work because of disabled token
            logout_response = self._get_with_user_token_auth(
                self.test_client, token, params={}, endpoint=self.test_endpoint)
            self.assertEqual(401, logout_response.status_code)
