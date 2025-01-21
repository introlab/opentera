from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest


class UserRefreshTokenTest(BaseUserAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/refresh_token'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(405, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.delete(self.test_endpoint)
            self.assertEqual(405, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(405, response.status_code)

    def test_post_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(405, response.status_code)

    def test_delete_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(405, response.status_code)

    def test_delete_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(405, response.status_code)

    def test_no_token_http_auth_refresh(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, token='')
            self.assertEqual(401, response.status_code)

    def test_valid_token_refresh(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     endpoint=self.login_endpoint)
            self.assertEqual(200, response.status_code)
            login_info = response.json
            self.assertTrue(login_info.__contains__('user_token'))
            token = login_info['user_token']
            response = self._get_with_user_token_auth(self.test_client, token=token)
            self.assertEqual(200, response.status_code)
            token_info = response.json
            self.assertTrue(token_info.__contains__('refresh_token'))
            refresh_token = token_info['refresh_token']
            self.assertGreater(len(refresh_token), 0)

    def test_invalid_token_refresh_with_disabled_token(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     endpoint=self.login_endpoint)
            self.assertEqual(200, response.status_code)
            login_info = response.json
            self.assertTrue(login_info.__contains__('user_token'))
            login_token = login_info['user_token']
            # Refresh token
            response = self._get_with_user_token_auth(self.test_client, token=login_token)
            self.assertEqual(200, response.status_code)
            token_info = response.json
            self.assertTrue(token_info.__contains__('refresh_token'))
            refresh_token = token_info['refresh_token']
            self.assertGreater(len(refresh_token), 0)
            # Login should not work, token should be disabled
            response = self._get_with_user_token_auth(self.test_client, token=login_token, endpoint=self.login_endpoint)
            self.assertEqual(401, response.status_code)

    def test_invalid_token_refresh_with_no_token(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     endpoint=self.login_endpoint)
            self.assertEqual(200, response.status_code)
            login_info = response.json
            self.assertTrue(login_info.__contains__('user_token'))
            login_token = login_info['user_token']
            response = self._get_with_user_token_auth(self.test_client, token='')
            self.assertEqual(401, response.status_code)
