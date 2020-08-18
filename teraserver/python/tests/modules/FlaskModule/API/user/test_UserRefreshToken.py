from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import datetime


class UserRefreshTokenTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/refresh_token'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_token_http_auth_refresh(self):
        response = self._request_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 401)

    def test_valid_token_refresh(self):
        response = self._login_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 200)
        login_info = response.json()
        self.assertTrue(login_info.__contains__('user_token'))
        token = login_info['user_token']
        response = self._request_with_token_auth(token=token)
        self.assertEqual(response.status_code, 200)
        token_info = response.json()
        self.assertTrue(token_info.__contains__('refresh_token'))
        refresh_token = token_info['refresh_token']
        self.assertGreater(len(refresh_token), 0)

    def test_invalid_token_refresh_with_disabled_token(self):
        response = self._login_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 200)
        login_info = response.json()
        self.assertTrue(login_info.__contains__('user_token'))
        login_token = login_info['user_token']
        response = self._request_with_token_auth(token=login_token)
        self.assertEqual(response.status_code, 200)
        token_info = response.json()
        self.assertTrue(token_info.__contains__('refresh_token'))
        refresh_token = token_info['refresh_token']
        self.assertGreater(len(refresh_token), 0)
        # This should not work, token should be disabled
        response = self._request_with_token_auth(token=login_token)
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_refresh_with_no_token(self):
        response = self._login_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 200)
        login_info = response.json()
        self.assertTrue(login_info.__contains__('user_token'))
        login_token = login_info['user_token']
        response = self._request_with_token_auth(token='')
        self.assertEqual(response.status_code, 401)
