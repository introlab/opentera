from tests.modules.FlaskModule.API.service.BaseServiceAPITest import BaseServiceAPITest

class ServiceQueryAuthCodeTest(BaseServiceAPITest):
    test_endpoint = '/api/service/auth/code'

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_with_wrong_params(self):
        with self._flask_app.app_context():
            params = {'invalid_param': 'invalid'}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                            params=params, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_with_endpoint_url_param(self):
        with self._flask_app.app_context():
            params = {'endpoint_url': '/testendpoint'}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertTrue('auth_code' in response.json)
