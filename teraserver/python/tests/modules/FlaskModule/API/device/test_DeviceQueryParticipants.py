from tests.modules.FlaskModule.API.device.BaseDeviceAPITest import BaseDeviceAPITest
from opentera.db.models.TeraDevice import TeraDevice


class DeviceQueryParticipantsTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/participants'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_with_invalid_token(self):
        with self._flask_app.app_context():
            response = self._get_with_device_token_auth(self.test_client, token='Invalid')
            self.assertEqual(response.status_code, 401)

    def test_get_endpoint_with_valid_token(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                response = self._get_with_device_token_auth(self.test_client, token=device.device_token)

                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                    continue

                if not device.device_onlineable:
                    self.assertEqual(response.status_code, 403)
                    continue

                self.assertEqual(response.status_code, 200)
                self.assertTrue('participants_info' in response.json)
