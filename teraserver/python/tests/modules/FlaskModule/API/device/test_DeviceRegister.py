import unittest
import os
from requests import get, post
import json


class DeviceRegisterTest(unittest.TestCase):

    host = 'localhost'
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

    def test_device_register_wrong_args_post(self):
        response = self._device_api_post(None, self.device_register_endpoint)
        self.assertEqual(response.status_code, 400)

    def test_device_register_ok_post(self):
        device_info = {'device_info': {'device_name': 'Device Name'}}
        response = self._device_api_post(None, self.device_register_endpoint, **device_info)
        self.assertEqual(200, response.status_code)

        token_dict = json.loads(response.text)
        self.assertTrue(token_dict.__contains__('token'))
        self.assertGreater(len(token_dict['token']), 0)

        # Validate that we cannot authenticate (device should be disabled)
        response = self._token_auth(token_dict['token'])
        self.assertEqual(response.status_code, 401)

