from BaseUserAPITest import BaseUserAPITest


class UserRefreshTokenTest(BaseUserAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/refresh_token'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

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
