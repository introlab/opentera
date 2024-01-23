from BaseDeviceAPITest import BaseDeviceAPITest
from opentera.db.models.TeraServerSettings import TeraServerSettings
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraDeviceSubType import TeraDeviceSubType
import opentera.crypto.crypto_utils as crypto
from cryptography.hazmat.primitives import serialization


class DeviceRegisterTest(BaseDeviceAPITest):

    test_endpoint = '/api/device/register'

    def setUp(self):
        super().setUp()
        self.sleep_time = 0
        with self._flask_app.app_context():
            self.device_register_key = (
                TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerDeviceRegisterKey)
            )

    def tearDown(self):
        super().tearDown()

    def test_register_token_missing_args(self):
        response = self._get_data_no_auth(self.test_client)
        self.assertEqual(400, response.status_code)

    def test_register_token_bad_key(self):
        data = {'key': 'Bad key',
                'name': 'New Device',
                'type_key': 'capteur'}
        response = self._get_data_no_auth(self.test_client, params=data)
        self.assertEqual(401, response.status_code)

    def test_register_token_existing_device_key(self):
        with self._flask_app.app_context():
            device_type_key = TeraDeviceType.get_device_type_by_id(1).device_type_key
            device_type_count = TeraDeviceType.get_count()
            data = {'key': self.device_register_key,
                    'name': 'New Device',
                    'type_key': device_type_key}
            response = self._get_data_no_auth(self.test_client, params=data)
            self.assertEqual(200, response.status_code)
            self._checkJson(response.json)

            device = TeraDevice.get_device_by_token(response.json['device_token'])
            self.assertIsNotNone(device)
            self.assertEqual('New Device', device.device_name)
            self.assertFalse(device.device_enabled)
            self.assertEqual(device_type_key, device.device_type.device_type_key)
            self.assertIsNone(device.id_device_subtype)
            self.assertEqual(device_type_count, TeraDeviceType.get_count())

    def test_register_token_existing_device_subtype(self):
        with self._flask_app.app_context():
            device_type_key = 'bureau_actif'
            device_type_count = TeraDeviceType.get_count()
            subtype_name = 'Bureau modèle #1'
            subtype_count = TeraDeviceSubType.get_count()
            data = {'key': self.device_register_key,
                    'name': 'New Device',
                    'type_key': device_type_key,
                    'subtype_name': subtype_name}
            response = self._get_data_no_auth(self.test_client, params=data)
            self.assertEqual(200, response.status_code)
            self._checkJson(response.json)

            device = TeraDevice.get_device_by_token(response.json['device_token'])
            self.assertIsNotNone(device)
            self.assertEqual('New Device', device.device_name)
            self.assertFalse(device.device_enabled)
            self.assertEqual(device_type_key, device.device_type.device_type_key)
            self.assertEqual(device_type_count, TeraDeviceType.get_count())
            self.assertEqual(subtype_name, device.device_subtype.device_subtype_name)
            self.assertEqual(subtype_count, TeraDeviceSubType.get_count())

    def test_register_token_new_device_key(self):
        with self._flask_app.app_context():
            device_type_key = 'New Token Device Type'
            device_type_count = TeraDeviceType.get_count()
            data = {'key': self.device_register_key,
                    'name': 'New Device',
                    'type_key': device_type_key}
            response = self._get_data_no_auth(self.test_client, params=data)
            self.assertEqual(200, response.status_code)
            self._checkJson(response.json)

            device = TeraDevice.get_device_by_token(response.json['device_token'])
            self.assertIsNotNone(device)
            self.assertEqual('New Device', device.device_name)
            self.assertFalse(device.device_enabled)
            self.assertEqual(device_type_key, device.device_type.device_type_key)
            self.assertIsNone(device.id_device_subtype)
            self.assertEqual(device_type_count+1, TeraDeviceType.get_count())

    def test_register_token_new_device_subtype(self):
        with self._flask_app.app_context():
            device_type_key = 'bureau_actif'
            device_type_count = TeraDeviceType.get_count()
            subtype_name = 'Bureau modèle #4'
            subtype_count = TeraDeviceSubType.get_count()
            data = {'key': self.device_register_key,
                    'name': 'New Device',
                    'type_key': device_type_key,
                    'subtype_name': subtype_name}
            response = self._get_data_no_auth(self.test_client, params=data)
            self.assertEqual(200, response.status_code)
            self._checkJson(response.json)

            device = TeraDevice.get_device_by_token(response.json['device_token'])
            self.assertIsNotNone(device)
            self.assertEqual('New Device', device.device_name)
            self.assertFalse(device.device_enabled)
            self.assertEqual(device_type_key, device.device_type.device_type_key)
            self.assertEqual(device_type_count, TeraDeviceType.get_count())
            self.assertEqual(subtype_name, device.device_subtype.device_subtype_name)
            self.assertEqual(subtype_count+1, TeraDeviceSubType.get_count())

    def test_register_certificate_bad_key(self):
        data = {'key': 'Bad key',
                'name': 'New Device',
                'type_key': 'capteur'}
        response = self._post_data_no_auth(self.test_client, params=data)
        self.assertEqual(401, response.status_code)

    def test_register_certificate_missing_args(self):
        response = self._post_data_no_auth(self.test_client)
        self.assertEqual(400, response.status_code)

    def test_register_certificate_existing_device_key(self):
        with self._flask_app.app_context():
            device_type_key = TeraDeviceType.get_device_type_by_id(1).device_type_key
            device_type_count = TeraDeviceType.get_count()
            data = {'key': self.device_register_key,
                    'name': 'New Device',
                    'type_key': device_type_key}
            # This will generate private key and signing request for the CA
            client_info = crypto.create_certificate_signing_request('Test Device with Certificate')

            # Encode in PEM format
            encoded_csr = client_info['csr'].public_bytes(serialization.Encoding.PEM)

            response = self._post_data_no_auth(self.test_client, data=encoded_csr, params=data)
            self.assertEqual(200, response.status_code)
            self._checkJson(response.json, True)

            device = TeraDevice.get_device_by_certificate(response.json['device_certificate'])
            self.assertIsNotNone(device)
            self.assertIsNotNone(device.device_certificate)
            self.assertEqual('New Device', device.device_name)
            self.assertFalse(device.device_enabled)
            self.assertEqual(device_type_key, device.device_type.device_type_key)
            self.assertEqual(device_type_count, TeraDeviceType.get_count())
            self.assertIsNone(device.id_device_subtype)

    def test_register_certificate_existing_device_subtype(self):
        with self._flask_app.app_context():
            device_type_key = 'bureau_actif'
            device_type_count = TeraDeviceType.get_count()
            subtype_name = 'Bureau modèle #1'
            subtype_count = TeraDeviceSubType.get_count()
            data = {'key': self.device_register_key,
                    'name': 'New Device',
                    'type_key': device_type_key,
                    'subtype_name': subtype_name}

            # This will generate private key and signing request for the CA
            client_info = crypto.create_certificate_signing_request('Test Device with Certificate')

            # Encode in PEM format
            encoded_csr = client_info['csr'].public_bytes(serialization.Encoding.PEM)

            response = self._post_data_no_auth(self.test_client, data=encoded_csr, params=data)
            self.assertEqual(200, response.status_code)
            self._checkJson(response.json, True)

            device = TeraDevice.get_device_by_certificate(response.json['device_certificate'])
            self.assertIsNotNone(device)
            self.assertEqual('New Device', device.device_name)
            self.assertFalse(device.device_enabled)
            self.assertEqual(device_type_key, device.device_type.device_type_key)
            self.assertEqual(device_type_count, TeraDeviceType.get_count())
            self.assertEqual(subtype_name, device.device_subtype.device_subtype_name)
            self.assertEqual(subtype_count, TeraDeviceSubType.get_count())

    def test_register_certificate_new_device_key(self):
        with self._flask_app.app_context():
            device_type_key = 'New Device Type'
            device_type_count = TeraDeviceType.get_count()
            data = {'key': self.device_register_key,
                    'name': 'New Device',
                    'type_key': device_type_key}
            # This will generate private key and signing request for the CA
            client_info = crypto.create_certificate_signing_request('Test Device with Certificate')

            # Encode in PEM format
            encoded_csr = client_info['csr'].public_bytes(serialization.Encoding.PEM)

            response = self._post_data_no_auth(self.test_client, data=encoded_csr, params=data)
            self.assertEqual(200, response.status_code)
            self._checkJson(response.json, True)

            device = TeraDevice.get_device_by_certificate(response.json['device_certificate'])
            self.assertIsNotNone(device)
            self.assertEqual('New Device', device.device_name)
            self.assertFalse(device.device_enabled)
            self.assertEqual(device_type_key, device.device_type.device_type_key)
            self.assertIsNone(device.id_device_subtype)
            self.assertEqual(device_type_count + 1, TeraDeviceType.get_count())

    def test_register_certificate_new_device_subtype(self):
        with self._flask_app.app_context():
            device_type_key = 'bureau_actif'
            device_type_count = TeraDeviceType.get_count()
            subtype_name = 'Bureau modèle #3'
            subtype_count = TeraDeviceSubType.get_count()
            data = {'key': self.device_register_key,
                    'name': 'New Device',
                    'type_key': device_type_key,
                    'subtype_name': subtype_name}
            # This will generate private key and signing request for the CA
            client_info = crypto.create_certificate_signing_request('Test Device with Certificate')

            # Encode in PEM format
            encoded_csr = client_info['csr'].public_bytes(serialization.Encoding.PEM)

            response = self._post_data_no_auth(self.test_client, data=encoded_csr, params=data)
            self.assertEqual(200, response.status_code)
            self._checkJson(response.json, True)

            device = TeraDevice.get_device_by_certificate(response.json['device_certificate'])
            self.assertIsNotNone(device)
            self.assertEqual('New Device', device.device_name)
            self.assertFalse(device.device_enabled)
            self.assertEqual(device_type_key, device.device_type.device_type_key)
            self.assertEqual(device_type_count, TeraDeviceType.get_count())
            self.assertEqual(subtype_name, device.device_subtype.device_subtype_name)
            self.assertEqual(subtype_count + 1, TeraDeviceSubType.get_count())

    def _checkJson(self, json_data, certificate=False):
        self.assertFalse(json_data.__contains__('id_device'))
        self.assertFalse(json_data.__contains__('id_device_type'))
        self.assertFalse(json_data.__contains__('id_device_subtype'))
        self.assertTrue(json_data.__contains__('device_name'))
        self.assertTrue(json_data.__contains__('device_uuid'))
        self.assertTrue(json_data.__contains__('device_token'))
        self.assertTrue(json_data.__contains__('device_enabled'))
        if certificate:
            self.assertTrue(json_data.__contains__('device_certificate'))
            self.assertTrue(json_data.__contains__('ca_info'))
