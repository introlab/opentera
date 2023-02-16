from BaseUserAPITest import BaseUserAPITest


class UserQueryVersionsTest(BaseUserAPITest):
    test_endpoint = '/api/user/versions'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_no_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client)
            self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(self.test_client, username='', password='')
            self.assertEqual(401, response.status_code)

    def test_query_get_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(200, response.status_code)
            value = response.json
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
