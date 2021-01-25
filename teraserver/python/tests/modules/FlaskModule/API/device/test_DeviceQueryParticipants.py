import unittest
import os
from requests import get
import json


class DeviceQueryParticipantsTest(unittest.TestCase):

    host = '127.0.0.1'
    port = 40075
    device_login_endpoint = '/api/device/login'
    device_logout_endpoint = '/api/device/logout'
    device_query_participants_endpoint = '/api/device/participants'
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

    def _token_auth_query_participants(self, token):
        url = self._make_url(self.host, self.port, self.device_query_participants_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def test_query_participants_get_with_valid_token(self):
        for device in self.all_devices:
            response = self._token_auth_query_participants(device['device_token'])
            if device['device_onlineable']:
                self.assertEqual(response.status_code, 200)
                participants = response.json()
                self.assertTrue(participants.__contains__('participants_info'))
            else:
                if not device['device_enabled']:
                    # Should return unauthorized
                    self.assertEqual(response.status_code, 401)
                else:
                    # Should return forbidden (not onlinable but enabled = forbidden)
                    self.assertEqual(response.status_code, 403)

    def test_query_participants_get_with_invalid_token(self):
        for device in self.all_devices:
            response = self._token_auth_query_participants(device['device_token'] + str('invalid'))
            # Should return unauthorized
            self.assertEqual(response.status_code, 401)
