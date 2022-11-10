from BaseDeviceAPITest import BaseDeviceAPITest
from opentera.db.models.TeraDevice import TeraDevice


class DeviceQueryDevicesTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/devices'

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
            response = self._get_with_device_token_auth(self.test_client, token='Invalid token')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_from_all_devices(self):
        with self._flask_app.app_context():
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

    def test_post_endpoint_from_all_devices_without_id_device(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                schema = {
                    'device':  {
                        # 'id_device': 32,
                        'device_config': 'Config string'
                        }
                }
                result = self._post_with_device_token_auth(self.test_client, token=device.device_token, json=schema)
                if not device.device_enabled:
                    self.assertEqual(result.status_code, 401)
                    continue

                self.assertEqual(result.status_code, 200)
                self.assertEqual(schema['device']['device_config'], result.json[0]['device_config'])
                # TODO why return an array
                self.assertEqual(device.id_device, result.json[0]['id_device'])

    def test_post_endpoint_from_all_devices_with_wrong_id_device(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                schema = {
                    'device': {
                        'id_device': 9999999999,
                        'device_config': 'Config string'
                    }
                }
                result = self._post_with_device_token_auth(self.test_client, token=device.device_token, json=schema)
                if not device.device_enabled:
                    self.assertEqual(result.status_code, 401)
                    continue

                # Should not be able to change another device id
                self.assertEqual(result.status_code, 403)

    def test_post_endpoint_from_all_devices_with_empty_schema(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                schema = {
                }
                result = self._post_with_device_token_auth(self.test_client, token=device.device_token, json=schema)
                if not device.device_enabled:
                    self.assertEqual(result.status_code, 401)
                    continue

                self.assertEqual(result.status_code, 400)
