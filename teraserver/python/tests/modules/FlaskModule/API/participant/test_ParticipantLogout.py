import unittest
import os
from requests import get
import json


class ParticipantLogoutTest(unittest.TestCase):
    host = '127.0.0.1'
    port = 40075
    logout_endpoint = '/api/participant/logout'
    login_endpoint = '/api/participant/login'

    def _make_url(self, hostname, port, endpoint):
        return 'https://' + hostname + ':' + str(port) + endpoint

    def _http_auth(self, username, password):
        url = self._make_url(self.host, self.port, self.login_endpoint)
        return get(url=url, verify=False, auth=(username, password))

    def _logout_token_auth(self, token):
        request_headers = {'Authorization': 'OpenTera ' + token}
        url = self._make_url(self.host, self.port, self.logout_endpoint)
        return get(url=url, verify=False, headers=request_headers)

    def _logout_http_auth(self, username, password):
        url = self._make_url(self.host, self.port, self.logout_endpoint)
        return get(url=url, verify=False, auth=(username, password))

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_logout_valid_participant_httpauth(self):
        # Using default participant information
        username = 'participant1'
        password = 'opentera'
        login_response = self._http_auth(username, password)
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.headers['Content-Type'], 'application/json')
        json_data = login_response.json()
        self.assertGreater(len(json_data), 0)

        logout_response = self._logout_http_auth(username, password)
        self.assertEqual(logout_response.headers['Content-Type'], 'application/json')
        self.assertEqual(logout_response.status_code, 200)

    def test_logout_invalid_participant_httpauth(self):
        username = 'invalid'
        password = 'invalid'
        login_response = self._http_auth(username, password)
        self.assertEqual(login_response.status_code, 401)

        logout_response = self._logout_http_auth(username, password)
        self.assertEqual(logout_response.headers['Content-Type'], 'application/json')
        self.assertEqual(logout_response.status_code, 200)

    def test_logout_valid_token_auth(self):
        # Get the token from http auth
        username = 'participant1'
        password = 'opentera'
        httpauth_response = self._http_auth(username, password)
        self.assertEqual(httpauth_response.status_code, 200)
        self.assertEqual(httpauth_response.headers['Content-Type'], 'application/json')
        json_data = httpauth_response.json()
        self.assertGreater(len(json_data), 0)

        # Try to logout when token is valid
        token = json_data['participant_token']
        self.assertGreater(len(token), 0)

        logout_response = self._logout_token_auth(token=token)
        self.assertEqual(logout_response.headers['Content-Type'], 'application/json')
        self.assertEqual(logout_response.status_code, 200)
