from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser


class UserLoginTest(BaseUserAPITest):
    test_endpoint = '/api/user/login'

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

    def test_get_endpoint_login_admin_user_http_auth(self):
        with self._flask_app.app_context():
            # Using default participant information
            response = self._get_with_user_http_auth(self.test_client, 'admin', 'admin')

            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertGreater(len(response.json), 0)

            # Validate fields in json response
            self.assertTrue('websocket_url' in response.json)
            self.assertTrue('user_uuid' in response.json)
            self.assertTrue('user_token' in response.json)

    def test_get_endpoint_login_admin_user_http_auth_then_token_auth(self):
        with self._flask_app.app_context():
            # Using default participant information
            response = self._get_with_user_http_auth(self.test_client, 'admin', 'admin')

            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertGreater(len(response.json), 0)

            # Validate fields in json response
            self.assertTrue('user_token' in response.json)
            token = response.json['user_token']

            # Now try with token authentication
            # Not allowed for this endpoint
            response = self._get_with_user_token_auth(self.test_client, token=token)
            self.assertEqual(401, response.status_code)
