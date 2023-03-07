from BaseDeviceAPITest import BaseDeviceAPITest
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceType import TeraDeviceType
import opentera.crypto.crypto_utils as crypto
from cryptography.hazmat.primitives import hashes, serialization
import time


class DeviceRegisterTest(BaseDeviceAPITest):

    test_endpoint = '/api/device/register'

    def setUp(self):
        super().setUp()
        self.sleep_time = 0

    def tearDown(self):
        super().tearDown()

    def test_post_endpoint_device_register_empty_json(self):
        with self._flask_app.app_context():
            # This is required since the server will throttle device creations
            time.sleep(self.sleep_time)

            response = self._post_data_no_auth(self.test_client, json={})
            self.assertEqual(response.status_code, 400)

    def test_post_endpoint_device_register_json_incomplete_post(self):
        with self._flask_app.app_context():
            # This is required since the server will throttle device creations
            time.sleep(self.sleep_time)

            device_info = {'device_info': {'device_name': 'Device Name'}}
            response = self._post_data_no_auth(self.test_client, json=device_info)
            self.assertEqual(response.status_code, 400)

            device_info = {'device_info': {'id_device_type': 0}}
            response = self._post_data_no_auth(self.test_client, json=device_info)
            self.assertEqual(response.status_code, 400)

    def test_post_endpoint_device_register_invalid_id_device_type(self):
        with self._flask_app.app_context():
            # This is required since the server will throttle device creations
            time.sleep(self.sleep_time)

            device_info = {'device_info': {'device_name': 'Device Name', 'id_device_type': 0}}
            response = self._post_data_no_auth(self.test_client, json=device_info)
            self.assertEqual(response.status_code, 500)

    def test_post_endpoint_device_register_json_ok(self):
        with self._flask_app.app_context():
            # This is required since the server will throttle device creations
            time.sleep(self.sleep_time)

            device_info = {'device_info': {'device_name': 'Device Name', 'id_device_type': 1}}
            response = self._post_data_no_auth(self.test_client, json=device_info)
            self.assertEqual(response.status_code, 200)
            self.assertTrue('token' in response.json)
            self.assertGreater(len(response.json['token']), 0)
            # Validate DB
            device: TeraDevice = TeraDevice.get_device_by_token(response.json['token'])
            self.assertIsNotNone(device)
            self.assertFalse(device.device_enabled)
            self.assertFalse(device.device_onlineable)
            self.assertEqual(device.id_device_type, 1)
            # Delete device
            TeraDevice.delete(device.id_device)
            self.assertIsNone(TeraDevice.get_device_by_token(response.json['token']))

    def test_post_endpoint_with_device_register_with_certificate_csr(self):
        with self._flask_app.app_context():
            # This is required since the server will throttle device creations
            time.sleep(self.sleep_time)

            # This will generate private key and signing request for the CA
            client_info = crypto.create_certificate_signing_request('Test Device with Certificate')

            # Encode in PEM format
            encoded_csr = client_info['csr'].public_bytes(serialization.Encoding.PEM)

            response = self._post_data_no_auth(self.test_client, data=encoded_csr)
            self.assertEqual(response.status_code, 200)

            self.assertTrue('ca_info' in response.json)
            self.assertTrue('certificate' in response.json)
            self.assertGreater(len(response.json['certificate']), 0)

            device: TeraDevice = TeraDevice.get_device_by_certificate(response.json['certificate'])
            self.assertIsNotNone(device)
            self.assertFalse(device.device_enabled)
            self.assertFalse(device.device_onlineable)
            # TODO device type default is 'capteur'
            self.assertEqual(device.id_device_type, TeraDeviceType.get_device_type_by_key('capteur').id_device_type)
            # Delete device
            TeraDevice.delete(device.id_device)
            self.assertIsNone(TeraDevice.get_device_by_certificate(response.json['certificate']))

