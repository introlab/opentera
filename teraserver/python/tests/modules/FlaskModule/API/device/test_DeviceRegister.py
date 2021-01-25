import unittest
import os
from requests import get, post
import json
import opentera.crypto.crypto_utils as crypto
from cryptography.hazmat.primitives import hashes, serialization


class DeviceRegisterTest(unittest.TestCase):

    host = '127.0.0.1'
    port = 40075
    device_login_endpoint = '/api/device/login'
    device_logout_endpoint = '/api/device/logout'
    device_register_endpoint = '/api/device/register'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _make_url(self, hostname, port, endpoint):
        return 'https://' + hostname + ':' + str(port) + endpoint

    def _token_auth(self, token):
        url = self._make_url(self.host, self.port, self.device_login_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def _certificate_auth(self, cert, key):
        url = self._make_url(self.host, self.port, self.device_login_endpoint)
        with open('cert.pem', 'wb') as f:
            f.write(cert)

        with open('key.pem', 'wb') as f:
            f.write(key)

        return get(url=url, verify=False, cert=('cert.pem', 'key.pem'))

    def _token_auth_logout(self, token):
        url = self._make_url(self.host, self.port, self.device_logout_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def _device_api_post(self, token, endpoint, **kwargs):
        url = self._make_url(self.host, self.port, endpoint)

        request_headers = {'Content-Type': 'application/json'}

        # Handle auth if required
        if token:
            request_headers['Authorization'] = 'OpenTera ' + token

        # post will convert dict to json automatically
        return post(url=url, verify=False, headers=request_headers, json=kwargs)

    def _device_api_certificate_post(self, cert, endpoint, **kwargs):
        url = self._make_url(self.host, self.port, endpoint)
        request_headers = {'Content-Type': 'application/octet-stream'}

    def _device_api_register_certificate_post(self, csr, endpoint, **kwargs):
        url = self._make_url(self.host, self.port, endpoint)
        request_headers = {'Content-Type': 'application/octet-stream',
                           'Content-Transfer-Encoding': 'Base64'}
        return post(url=url, verify=False, headers=request_headers, data=csr)

    def test_device_register_wrong_args_post(self):
        response = self._device_api_post(None, self.device_register_endpoint)
        self.assertEqual(response.status_code, 400)

    def test_device_register_incomplete_post(self):
        device_info = {'device_info': {'device_name': 'Device Name'}}
        response = self._device_api_post(None, self.device_register_endpoint, **device_info)
        self.assertEqual(400, response.status_code)

        device_info = {'device_info': {'id_device_type': 0}}
        response = self._device_api_post(None, self.device_register_endpoint, **device_info)
        self.assertEqual(400, response.status_code)

    def test_device_register_invalid_id_device_type(self):
        device_info = {'device_info': {'device_name': 'Device Name', 'id_device_type': 0}}
        response = self._device_api_post(None, self.device_register_endpoint, **device_info)
        self.assertEqual(500, response.status_code)

    def test_device_register_ok_post(self):
        device_info = {'device_info': {'device_name': 'Device Name', 'id_device_type': 1}}
        response = self._device_api_post(None, self.device_register_endpoint, **device_info)
        self.assertEqual(200, response.status_code)

        token_dict = json.loads(response.text)
        self.assertTrue(token_dict.__contains__('token'))
        self.assertGreater(len(token_dict['token']), 0)

        # Validate that we cannot authenticate (device should be disabled)
        response = self._token_auth(token_dict['token'])
        self.assertEqual(response.status_code, 401)

    def test_device_register_with_certificate_csr(self):

        # This is required since the server will throttle device creations
        import time
        time.sleep(1)

        # This will generate private key and signing request for the CA
        client_info = crypto.create_certificate_signing_request('Test Device with Certificate')

        # Encode in PEM format
        encoded_csr = client_info['csr'].public_bytes(serialization.Encoding.PEM)

        response = self._device_api_register_certificate_post(encoded_csr, self.device_register_endpoint)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertTrue('ca_info' in result)
        self.assertTrue('certificate' in result)

        certificate = result['certificate'].encode('utf-8')
        private_key = client_info['private_key'].private_bytes(serialization.Encoding.PEM,
                                                               serialization.PrivateFormat.TraditionalOpenSSL,
                                                               serialization.NoEncryption())

        # print(certificate, private_key)
        response = self._certificate_auth(certificate, private_key)
        self.assertTrue(response.status_code, 200)



