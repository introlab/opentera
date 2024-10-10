from tests.modules.FlaskModule.API.device.BaseDeviceAPITest import BaseDeviceAPITest
from opentera.db.models.TeraDevice import TeraDevice


class DeviceLoginTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/login'

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
                        self.assertEqual(200, response.status_code)

                        self.assertTrue('device_info' in response.json)
                        self.assertTrue('participants_info' in response.json)
                        self.assertTrue('session_types_info' in response.json)
                        self.assertEqual(device['id_device'], response.json['device_info']['id_device'])
                        self.assertTrue('device_type' in response.json['device_info'])

                        if device['device_onlineable']:
                            self.assertTrue('websocket_url' in response.json)

                    else:
                        response = self._get_with_device_token_auth(self.test_client, token=device['device_token'])
                        self.assertEqual(401, response.status_code)
