import unittest
import os
from requests import get
import json


class DeviceQueryDevicesTest(unittest.TestCase):

    host = '127.0.0.1'
    port = 40075
    device_login_endpoint = '/api/device/login'
    device_logout_endpoint = '/api/device/logout'
    device_query_devices_endpoint = '/api/device/devices'
    user_device_endpoint = '/api/user/devices'
    all_devices = None

    def setUp(self):
        # Use admin account to get device information (and tokens)
        response = self._http_auth_devices('admin', 'admin')
        self.assertEqual(response.status_code, 200)
        self.all_devices = json.loads(response.text)
        self.assertGreater(len(self.all_devices), 0)

    def tearDown(self):
        pass

    def _make_url(self, hostname, port, endpoint):
        return 'https://' + hostname + ':' + str(port) + endpoint

    def _http_auth_devices(self, username, password):
        url = self._make_url(self.host, self.port, self.user_device_endpoint)
        return get(url=url, verify=False, auth=(username, password))

    def _token_auth(self, token):
        url = self._make_url(self.host, self.port, self.device_login_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def _token_auth_logout(self, token):
        url = self._make_url(self.host, self.port, self.device_logout_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def _token_auth_query_devices(self, token):
        url = self._make_url(self.host, self.port, self.device_query_devices_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def test_query_devices_get(self):
        for device in self.all_devices:
            response = self._token_auth_query_devices(device['device_token'])
            if device['device_enabled']:
                self.assertEqual(response.status_code, 200)
                info = json.loads(response.text)
                self.assertTrue(info.__contains__('device_info'))
                self.assertTrue(info.__contains__('participants_info'))
                self.assertTrue(info.__contains__('session_types_info'))
                self.assertEqual(device['id_device'], info['device_info']['id_device'])
            else:
                self.assertEqual(response.status_code, 401)
