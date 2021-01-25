import unittest
import os
from requests import get
import json


class DeviceUploadTest(unittest.TestCase):

    host = '127.0.0.1'
    port = 40075
    device_login_endpoint = '/api/device/login'
    device_logout_endpoint = '/api/device/logout'
    device_query_session_endpoint = '/api/device/sessions'
    device_query_session_events_endpoint = '/api/device/sessionevents'
    user_device_endpoint = '/api/user/devices'
    all_devices = None

    def setUp(self):
        # Use admin account to get device information (and tokens)
        response = self._http_auth_devices('admin', 'admin')
        self.assertEqual(response.status_code, 200)
        self.all_devices = json.loads(response.text)
        self.assertGreater(len(self.all_devices), 0)

        # Populate sessions for all devices
        # for device in self.all_devices:
        #     response_sessions = self._token_auth_query_sessions(device['device_token'])
        #     self.assertEqual(response_sessions.status_code, 200)

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

    def _token_auth_query_sessions(self, token):
        url = self._make_url(self.host, self.port, self.device_query_session_endpoint) + '?list=true'
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def test_device_upload_get(self):
        # TODO
        pass
