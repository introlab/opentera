from BaseDeviceAPITest import BaseDeviceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraDevice import TeraDevice


class DeviceQueryParticipantsTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/participants'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import device_api_ns
        from BaseDeviceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.device.DeviceQueryParticipants import DeviceQueryParticipants
        kwargs = {
            'flaskModule': FakeFlaskModule(config=BaseDeviceAPITest.getConfig()),
            'test': True
        }
        device_api_ns.add_resource(DeviceQueryParticipants, '/participants', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_with_invalid_token(self):
        with flask_app.app_context():
            response = self._get_with_device_token_auth(self.test_client, token='Invalid')
            self.assertEqual(response.status_code, 401)

    def test_get_endpoint_with_valid_token(self):
        with flask_app.app_context():
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
