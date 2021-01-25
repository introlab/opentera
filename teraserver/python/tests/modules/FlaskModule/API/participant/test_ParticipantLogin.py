import unittest
import os
from requests import get
import json


class ParticipantLoginTest(unittest.TestCase):

    host = '127.0.0.1'
    port = 40075
    login_endpoint = '/api/participant/login'

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

    def test_login_valid_participant_httpauth(self):
        # Using default participant information
        backend_response = self._http_auth('participant1', 'opentera')
        self.assertEqual(backend_response.status_code, 200)
        self.assertEqual(backend_response.headers['Content-Type'], 'application/json')
        json_data = backend_response.json()
        self.assertGreater(len(json_data), 0)

        # Validate fields in json response
        self.assertTrue(json_data.__contains__('websocket_url'))
        self.assertTrue(json_data.__contains__('participant_uuid'))
        self.assertTrue(json_data.__contains__('participant_token'))
        self.assertTrue(json_data.__contains__('base_token'))
        self.assertGreater(len(json_data['websocket_url']), 0)
        self.assertGreater(len(json_data['participant_uuid']), 0)
        self.assertGreater(len(json_data['participant_token']), 0)
        self.assertGreater(len(json_data['base_token']), 0)

    def test_login_invalid_participant_httpauth(self):
        backend_response = self._http_auth('invalid', 'invalid')
        self.assertEqual(backend_response.status_code, 401)

    def test_login_valid_token_auth(self):
        # Get the token from http auth
        httpauth_response = self._http_auth('participant1', 'opentera')
        self.assertEqual(httpauth_response.status_code, 200)
        self.assertEqual(httpauth_response.headers['Content-Type'], 'application/json')
        json_data = httpauth_response.json()
        self.assertGreater(len(json_data), 0)

        # Try to login with token
        token = json_data['participant_token']
        self.assertGreater(len(token), 0)
        tokenauth_response = self._token_auth(token)
        self.assertEqual(tokenauth_response.status_code, 200)

    def test_login_base_token_auth(self):
        # Get the token from http auth
        httpauth_response = self._http_auth('participant1', 'opentera')
        self.assertEqual(httpauth_response.status_code, 200)
        self.assertEqual(httpauth_response.headers['Content-Type'], 'application/json')
        json_data = httpauth_response.json()
        self.assertGreater(len(json_data), 0)

        # Try to login with token
        token = json_data['base_token']
        self.assertGreater(len(token), 0)
        tokenauth_response = self._token_auth(token)
        self.assertEqual(tokenauth_response.status_code, 200)
        json_data = tokenauth_response.json()
        self.assertTrue('base_token' in json_data)
        self.assertTrue('participant_token' in json_data)
        self.assertGreater(len(json_data['base_token']), 0)
        self.assertIsNone(json_data['participant_token'])
