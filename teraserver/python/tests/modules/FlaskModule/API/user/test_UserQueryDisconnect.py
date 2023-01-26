from BaseUserAPITest import BaseUserAPITest


class UserQueryFormsTest(BaseUserAPITest):
    test_endpoint = '/api/user/users/disconnect'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)
