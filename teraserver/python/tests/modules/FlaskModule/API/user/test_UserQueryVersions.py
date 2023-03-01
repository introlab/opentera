from BaseUserAPITest import BaseUserAPITest
from opentera.utils.TeraVersions import TeraVersions


class UserQueryVersionsTest(BaseUserAPITest):
    test_endpoint = '/api/user/versions'

    def setUp(self):
        super().setUp()

        with self._flask_app.app_context():
            # Set versions
            versions = TeraVersions()

            # Will update clients versions (hard coded in TeraVersions)
            versions.load_from_db()
            versions.save_to_db()

    def tearDown(self):
        super().tearDown()

    def test_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

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
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

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
