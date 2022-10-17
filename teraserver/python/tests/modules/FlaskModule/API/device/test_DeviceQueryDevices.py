from BaseDeviceAPITest import BaseDeviceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraDevice import TeraDevice


class DeviceQueryDevicesTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/devices'

    def setUp(self):

        super().setUp()
        from modules.FlaskModule.FlaskModule import device_api_ns
        from BaseDeviceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.device.DeviceQueryDevices import DeviceQueryDevices
        kwargs = {
            'flaskModule': FakeFlaskModule(config=BaseDeviceAPITest.getConfig()),
            'test': True
        }
        device_api_ns.add_resource(DeviceQueryDevices, '/devices', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_from_all_devices(self):
        with flask_app.app_context():
            for device in TeraDevice.query.all():
                response = self._get_with_device_token_auth(self.test_client, token=device.device_token)
                if not device.device_enabled:
                    self.assertEqual(401, response.status_code)
                    # Next device
                    continue

                self.assertEqual(200, response.status_code)
                self.assertTrue('device_info' in response.json)
                self.assertTrue('participants_info' in response.json)
                self.assertTrue('session_types_info' in response.json)

                minimal_fields = ['device_enabled', 'device_name', 'device_uuid', 'id_device', 'id_device_subtype',
                                  'id_device_type']
                for field in minimal_fields:
                    self.assertTrue(field in response.json['device_info'])

                ignore_fields = ['device_projects', 'device_participants', 'device_sessions', 'device_certificate',
                                 'device_type', 'device_subtype', 'authenticated', 'device_assets', 'device_sites',
                                 'device_onlineable', 'device_config', 'device_notes', 'device_lastonline',
                                 'device_infos', 'device_token']
                for field in ignore_fields:
                    self.assertFalse(field in response.json['device_info'])
