from BaseDeviceAPITest import BaseDeviceAPITest
from opentera.db.models.TeraDevice import TeraDevice


class DeviceLogoutTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/logout'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_device_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth(self):
        with self._flask_app.app_context():
            devices = []
            # Warning, device is updated on login, ORM will render the object "dirty".
            for device in TeraDevice.query.all():
                devices.append(device.to_json(minimal=False))

            for device in devices:
                if device['device_token']:
                    if device['device_enabled']:
                        response = self._get_with_device_token_auth(self.test_client, token=device['device_token'])
                        self.assertEqual(403, response.status_code)
                    else:
                        response = self._get_with_device_token_auth(self.test_client, token=device['device_token'])
                        self.assertEqual(401, response.status_code)
