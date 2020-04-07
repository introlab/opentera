import unittest
import os
from requests import get
import json


class DeviceQuerySessionEvents(unittest.TestCase):

    host = 'localhost'
    port = 4040
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
        for device in self.all_devices:
            response_sessions = self._token_auth_query_sessions(device['device_token'])
            self.assertEqual(response_sessions.status_code, 200)
            device['sessions'] = json.loads(response_sessions.text)
            print(device['sessions'])

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

    def _token_auth_query_session_events(self, token, id_session=None):
        url = self._make_url(self.host, self.port, self.device_query_session_events_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        if id_session:
            url = url + '?id_session=' + str(id_session)

        return get(url=url, verify=False, headers=request_headers)

    def test_query_session_events_get_without_session_id(self):
        for device in self.all_devices:
            response = self._token_auth_query_session_events(device['device_token'])
            self.assertEqual(response.status_code, 400)
            errors = json.loads(response.text)
            self.assertGreater(len(errors), 0)

    def test_query_session_events_get_wrong_session_id(self):
        for device in self.all_devices:
            response = self._token_auth_query_session_events(device['device_token'], -1)
            self.assertEqual(response.status_code, 403)

    def test_query_session_event_get_invalid_args(self):
        for device in self.all_devices:
            # Custom request
            url = self._make_url(self.host, self.port, self.device_query_session_events_endpoint) + '?invalid=True'
            request_headers = {'Authorization': 'OpenTera ' + device['device_token']}
            response = get(url=url, verify=False, headers=request_headers)
            self.assertEqual(response.status_code, 400)

    def test_query_session_event_get_valid_session_id(self):
        for device in self.all_devices:
            for session in device['sessions']:
                response = self._token_auth_query_session_events(device['device_token'], session['id_session'])
                self.assertEqual(response.status_code, 200)
                # TODO to something with session events
