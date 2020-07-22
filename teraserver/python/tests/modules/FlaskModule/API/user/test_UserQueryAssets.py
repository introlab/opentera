from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest

import datetime


class UserQueryAssetsTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/assets'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_auth(self):
        response = self._request_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_post_no_auth(self):
        response = self._post_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_delete_no_auth(self):
        response = self._delete_with_no_auth(id_to_del=0)
        self.assertEqual(response.status_code, 401)

    def test_query_no_params_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 400)

    def test_query_tera_server_assets_as_admin(self):
        payload = {'service_uuid': '00000000-0000-0000-0000-000000000001'}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload)

        self.assertEqual(response.status_code, 200)
