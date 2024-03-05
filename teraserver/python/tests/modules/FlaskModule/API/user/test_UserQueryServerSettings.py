from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraServerSettings import TeraServerSettings


class UserQueryServerSettingsTest(BaseUserAPITest):
    test_endpoint = '/api/user/server/settings'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(405, response.status_code)

    def test_delete(self):
        with self._flask_app.app_context():
            response = self.test_client.delete(self.test_endpoint)
            self.assertEqual(405, response.status_code)

    def test_get_server_uuid(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, 'user', 'user', {'uuid': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue('server_uuid' in response.json)
            server_uuid = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerUUID)
            self.assertEqual(server_uuid, response.json['server_uuid'])

    def test_get_device_register_key(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, 'user3', 'user3', {'device_register_key': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue('device_register_key' in response.json)
            key = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerDeviceRegisterKey)
            self.assertEqual(key, response.json['device_register_key'])

    def test_get_nothing(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, 'siteadmin', 'siteadmin')
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json) == 0)

    def test_get_server_uuid_and_device_register_key(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, 'admin', 'admin', {'uuid': True,
                                                                                          'device_register_key': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue('server_uuid' in response.json)
            self.assertTrue('device_register_key' in response.json)
            server_uuid = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerUUID)
            self.assertEqual(server_uuid, response.json['server_uuid'])
            key = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerDeviceRegisterKey)
            self.assertEqual(key, response.json['device_register_key'])
