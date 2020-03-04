import unittest
import os
from requests import get
import json


class ParticipantQuerySessionsTest(unittest.TestCase):

    host = 'localhost'
    port = 4040
    login_endpoint = '/api/participant/login'
    sessions_endpoint = '/api/participant/sessions'

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

    def _request_with_http_auth(self, username, password, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.sessions_endpoint)
        return get(url=url, verify=False, auth=(username, password), params=payload)

    def _request_with_token_auth(self, token, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.sessions_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers, params=payload)

    def _request_with_no_auth(self, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.sessions_endpoint)
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

        for data_item in json_data:
            self.assertGreater(len(data_item), 0)
            self.assertTrue(data_item.__contains__('id_creator_device'))
            self.assertTrue(data_item.__contains__('id_creator_participant'))
            self.assertTrue(data_item.__contains__('id_creator_user'))
            self.assertTrue(data_item.__contains__('id_session'))
            self.assertTrue(data_item.__contains__('id_session_type'))
            self.assertTrue(data_item.__contains__('session_comments'))
            self.assertTrue(data_item.__contains__('session_duration'))
            self.assertTrue(data_item.__contains__('session_name'))
            self.assertTrue(data_item.__contains__('session_start_datetime'))
            self.assertTrue(data_item.__contains__('session_status'))
            self.assertTrue(data_item.__contains__('session_participants_ids'))
            self.assertTrue(data_item.__contains__('session_creator_user'))
            self.assertTrue(data_item.__contains__('session_has_device_data'))

    def test_query_token_auth_no_params(self):
        # HTTP AUTH REQUIRED TO GET TOKEN
        token = self._get_token_with_login_http_auth('participant1', 'opentera')

        response = self._request_with_token_auth(token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        for data_item in json_data:
            self.assertGreater(len(data_item), 0)
            self.assertTrue(data_item.__contains__('id_creator_device'))
            self.assertTrue(data_item.__contains__('id_creator_participant'))
            self.assertTrue(data_item.__contains__('id_creator_user'))
            self.assertTrue(data_item.__contains__('id_session'))
            self.assertTrue(data_item.__contains__('id_session_type'))
            self.assertTrue(data_item.__contains__('session_comments'))
            self.assertTrue(data_item.__contains__('session_duration'))
            self.assertTrue(data_item.__contains__('session_name'))
            self.assertTrue(data_item.__contains__('session_start_datetime'))
            self.assertTrue(data_item.__contains__('session_status'))
            self.assertTrue(data_item.__contains__('session_participants_ids'))
            self.assertTrue(data_item.__contains__('session_creator_user'))
            self.assertTrue(data_item.__contains__('session_has_device_data'))