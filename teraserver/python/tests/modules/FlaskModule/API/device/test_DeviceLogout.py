from BaseDeviceAPITest import BaseDeviceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraDevice import TeraDevice


class DeviceLogoutTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/logout'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import device_api_ns
        from BaseDeviceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.device.DeviceLogout import DeviceLogout
        kwargs = {
            'flaskModule': FakeFlaskModule(config=BaseDeviceAPITest.getConfig()),
            'test': True
        }
        device_api_ns.add_resource(DeviceLogout, '/logout', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        response = self.test_client.get(self.test_endpoint)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        response = self._get_with_device_token_auth(self.test_client, token='invalid')
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth(self):
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
