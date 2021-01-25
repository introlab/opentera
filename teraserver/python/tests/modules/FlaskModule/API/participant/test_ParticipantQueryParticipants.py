import unittest
import os
from requests import get
import json


class ParticipantQueryParticipantsTest(unittest.TestCase):

    host = '127.0.0.1'
    port = 40075
    login_endpoint = '/api/participant/login'
    participants_endpoint = '/api/participant/participants'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _make_url(self, hostname, port, endpoint):
        return 'https://' + hostname + ':' + str(port) + endpoint

    def _get_token_with_login_http_auth(self, username, password):
        url = self._make_url(self.host, self.port, self.login_endpoint)
        auth_response = get(url=url, verify=False, auth=(username, password))
        # HTTP AUTH REQUIRED TO GET TOKEN
        self.assertEqual(auth_response.status_code, 200)
        self.assertEqual(auth_response.headers['Content-Type'], 'application/json')
        json_auth = auth_response.json()
        self.assertTrue(json_auth.__contains__('participant_token'))
        return json_auth['participant_token']

    def _get_base_token_with_login_http_auth(self, username, password):
        url = self._make_url(self.host, self.port, self.login_endpoint)
        auth_response = get(url=url, verify=False, auth=(username, password))
        # HTTP AUTH REQUIRED TO GET TOKEN
        self.assertEqual(auth_response.status_code, 200)
        self.assertEqual(auth_response.headers['Content-Type'], 'application/json')
        json_auth = auth_response.json()
        self.assertTrue(json_auth.__contains__('base_token'))
        return json_auth['base_token']

    def _request_with_http_auth(self, username, password, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.participants_endpoint)
        return get(url=url, verify=False, auth=(username, password), params=payload)

    def _request_with_token_auth(self, token, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.participants_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers, params=payload)

    def _request_with_no_auth(self, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.participants_endpoint)
        return get(url=url, verify=False, params=payload)

    def test_query_invalid_http_auth(self):
        response = self._request_with_http_auth('invalid', 'invalid')
        self.assertEqual(response.status_code, 401)

    def test_query_invalid_token_auth(self):
        response = self._request_with_token_auth('invalid')
        self.assertEqual(response.status_code, 401)

    def test_query_http_auth_no_params(self):
        response = self._request_with_http_auth('participant1', 'opentera')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_participant'))
        self.assertTrue(json_data.__contains__('id_participant_group'))
        self.assertTrue(json_data.__contains__('id_project'))
        self.assertTrue(json_data.__contains__('participant_email'))
        self.assertTrue(json_data.__contains__('participant_enabled'))
        # self.assertTrue(json_data.__contains__('participant_lastonline'))
        # self.assertTrue(json_data.__contains__('participant_login_enabled'))
        self.assertTrue(json_data.__contains__('participant_name'))
        # self.assertTrue(json_data.__contains__('participant_username'))
        # self.assertTrue(json_data.__contains__('participant_uuid'))
        self.assertFalse(json_data.__contains__('participant_password'))

    def test_query_token_auth_no_params(self):
        # HTTP AUTH REQUIRED TO GET TOKEN
        token = self._get_token_with_login_http_auth('participant1', 'opentera')

        response = self._request_with_token_auth(token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_participant'))
        self.assertTrue(json_data.__contains__('id_participant_group'))
        self.assertTrue(json_data.__contains__('id_project'))
        self.assertTrue(json_data.__contains__('participant_email'))
        self.assertTrue(json_data.__contains__('participant_enabled'))
        # self.assertTrue(json_data.__contains__('participant_lastonline'))
        # self.assertTrue(json_data.__contains__('participant_login_enabled'))
        self.assertTrue(json_data.__contains__('participant_name'))
        # self.assertTrue(json_data.__contains__('participant_username'))
        # self.assertTrue(json_data.__contains__('participant_uuid'))
        self.assertFalse(json_data.__contains__('participant_password'))

    def test_query_http_auth_invalid_params(self):
        params = {
            'invalid': 1
        }
        response = self._request_with_http_auth('participant1', 'opentera', params)
        self.assertEqual(response.status_code, 400)

    def test_query_http_auth_list_param(self):
        params = {
            'list': True
        }
        response = self._request_with_http_auth('participant1', 'opentera', params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

    def test_query_base_token(self):
        token = self._get_base_token_with_login_http_auth('participant1', 'opentera')
        response = self._request_with_token_auth(token)
        # Should not be allowed
        self.assertEqual(response.status_code, 403)
