import unittest
import os
from requests import get
import json


class ParticipantRefreshTokenTest(unittest.TestCase):

    host = '127.0.0.1'
    port = 40075
    login_endpoint = '/api/participant/login'
    refresh_token_endpoint = '/api/participant/refresh_token'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _make_url(self, hostname, port, endpoint):
        return 'https://' + hostname + ':' + str(port) + endpoint

    def _http_auth(self, username, password):
        url = self._make_url(self.host, self.port, self.login_endpoint)
        return get(url=url, verify=False, auth=(username, password))

    def _token_auth(self, token):
        url = self._make_url(self.host, self.port, self.login_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def _refresh_token(self, token):
        url = self._make_url(self.host, self.port, self.refresh_token_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers)

    def test_valid_refresh_token(self):
        # Get the token from http auth
        httpauth_response = self._http_auth('participant1', 'opentera')
        self.assertEqual(httpauth_response.status_code, 200)
        self.assertEqual(httpauth_response.headers['Content-Type'], 'application/json')
        json_data = httpauth_response.json()
        self.assertGreater(len(json_data), 0)
        self.assertTrue('participant_token' in json_data)
        login_token = json_data['participant_token']
        self.assertGreater(len(login_token), 0)

        # Try to refresh token
        response = self._refresh_token(login_token)
        self.assertEqual(response.status_code, 200)
        refresh_info = response.json()
        self.assertTrue('refresh_token' in refresh_info)

    def test_invalid_refresh_token(self):
        # Try to refresh token
        response = self._refresh_token('')
        self.assertEqual(response.status_code, 401)

    def test_invalid_refresh_token_from_disabled_token(self):
        # Get the token from http auth
        httpauth_response = self._http_auth('participant1', 'opentera')
        self.assertEqual(httpauth_response.status_code, 200)
        self.assertEqual(httpauth_response.headers['Content-Type'], 'application/json')
        json_data = httpauth_response.json()
        self.assertGreater(len(json_data), 0)
        self.assertTrue('participant_token' in json_data)
        login_token = json_data['participant_token']
        self.assertGreater(len(login_token), 0)

        # Try to refresh token, should work
        response = self._refresh_token(login_token)
        self.assertEqual(response.status_code, 200)
        refresh_info = response.json()
        self.assertTrue('refresh_token' in refresh_info)

        # Try to refresh same login token, should not work because it is disabled
        response = self._refresh_token(login_token)
        self.assertEqual(response.status_code, 401)
