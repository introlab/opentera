import unittest
import os
from requests import get
import json


class DeviceQueryAssetsTest(unittest.TestCase):

    host = '127.0.0.1'
    port = 40075
    device_login_endpoint = '/api/device/login'
    device_logout_endpoint = '/api/device/logout'
    device_query_assets_endpoint = '/api/device/assets'
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

    def _token_auth_query_assets(self, token):
        url = self._make_url(self.host, self.port, self.device_query_assets_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def test_query_assets_get(self):
        for device in self.all_devices:
            if device['device_enabled']:
                response = self._token_auth_query_assets(device['device_token'])
                # Should be forbidden
                self.assertEqual(response.status_code, 403)
                # assets = json.loads(response.text)
                # self.assertTrue(assets.__contains__('device_assets'))
                # for asset in assets['device_assets']:
                #     print(asset)
                #     # TODO Validate Asset JSON
            else:
                # Device not enabled should return access denied
                response = self._token_auth_query_assets(device['device_token'])
                self.assertEqual(response.status_code, 401)

    def test_query_assets_post(self):
        pass