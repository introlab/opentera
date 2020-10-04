from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest

import datetime


class UserQueryVersions(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/versions'

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

    def test_query_get_no_params_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 200)
        value = response.json()
        self.assertTrue('version_string' in value)
        self.assertTrue('version_major' in value)
        self.assertTrue('version_minor' in value)
        self.assertTrue('version_patch' in value)
        self.assertTrue('clients' in value)

        # Test for clients
        for client_name in value['clients']:
            client = value['clients'][client_name]
            self.assertTrue('client_name' in client)
            self.assertTrue('client_description' in client)
            self.assertTrue('client_version' in client)
            self.assertTrue('client_windows_download_url' in client)
            self.assertTrue('client_mac_download_url' in client)
            self.assertTrue('client_linux_download_url' in client)
