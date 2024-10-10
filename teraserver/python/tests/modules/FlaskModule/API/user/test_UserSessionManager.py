from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest


class UserSessionManagerTest(BaseUserAPITest):
    test_endpoint = '/api/user/sessions/manager'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(405, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.delete(self.test_endpoint)
            self.assertEqual(405, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(405, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(405, response.status_code)

    def test_post_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(405, response.status_code)

    def test_delete_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(405, response.status_code)
