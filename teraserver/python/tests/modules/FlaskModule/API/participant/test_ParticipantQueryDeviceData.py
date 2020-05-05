import unittest
import os
from requests import get
import json


class ParticipantQueryDeviceDataTest(unittest.TestCase):
    host = 'localhost'
    port = 40075
    login_endpoint = '/api/participant/login'
    data_endpoint = '/api/participant/data'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _get_token_with_login_http_auth(self, username, password):
        url = self._make_url(self.host, self.port, self.login_endpoint)
        auth_response = get(url=url, verify=False, auth=(username, password))
        # HTTP AUTH REQUIRED TO GET TOKEN
        self.assertEqual(auth_response.status_code, 200)
        self.assertEqual(auth_response.headers['Content-Type'], 'application/json')
        json_auth = auth_response.json()
        self.assertTrue(json_auth.__contains__('participant_token'))
        return json_auth['participant_token']

    def _make_url(self, hostname, port, endpoint):
        return 'https://' + hostname + ':' + str(port) + endpoint

    def _request_with_http_auth(self, username, password, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.data_endpoint)
        return get(url=url, verify=False, auth=(username, password), params=payload)

    def _request_with_token_auth(self, token, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.data_endpoint)
        request_headers = {'Authorization': 'OpenTera ' + token}
        return get(url=url, verify=False, headers=request_headers, params=payload)

    def _request_with_no_auth(self, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.data_endpoint)
        return get(url=url, verify=False, params=payload)

    def test_query_http_auth_no_params(self):
        response = self._request_with_http_auth('participant1', 'opentera')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        for data_item in json_data:
            self.assertGreater(len(data_item), 0)
            self.assertTrue(data_item.__contains__('devicedata_filesize'))
            self.assertTrue(data_item.__contains__('devicedata_name'))
            self.assertTrue(data_item.__contains__('devicedata_original_filename'))
            self.assertTrue(data_item.__contains__('devicedata_saved_date'))
            self.assertTrue(data_item.__contains__('id_device'))
            self.assertTrue(data_item.__contains__('id_device_data'))
            self.assertTrue(data_item.__contains__('id_session'))

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
            self.assertTrue(data_item.__contains__('devicedata_filesize'))
            self.assertTrue(data_item.__contains__('devicedata_name'))
            self.assertTrue(data_item.__contains__('devicedata_original_filename'))
            self.assertTrue(data_item.__contains__('devicedata_saved_date'))
            self.assertTrue(data_item.__contains__('id_device'))
            self.assertTrue(data_item.__contains__('id_device_data'))
            self.assertTrue(data_item.__contains__('id_session'))

    def test_query_invalid_http_auth(self):
        response = self._request_with_http_auth('invalid', 'invalid')
        self.assertEqual(response.status_code, 401)

    def test_query_invalid_token_auth(self):
        response = self._request_with_token_auth('invalid')
        self.assertEqual(response.status_code, 401)

    def test_query_http_auth_all_params(self):
        params = {
            'id_device_data': 1,
            'id_device': 1,
            'id_session': 1,
            'download': False
        }
        response = self._request_with_http_auth('participant1', 'opentera', params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

    def test_query_http_auth_illegal_params(self):
        params = {
            'id_device_data': 1,
            'id_device': 1,
            'id_session': 1,
            'download': False,
            'illegal': 'illegal'
        }
        response = self._request_with_http_auth('participant1', 'opentera', params)
        self.assertEqual(response.status_code, 400)

    def test_query_http_auth_all_params_download(self):
        params = {
            'id_device_data': 1,
            'id_device': 1,
            'id_session': 1,
            'download': True
        }
        response = self._request_with_http_auth('participant1', 'opentera', params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/octet-stream')
        length = int(response.headers['Content-Length'])
        self.assertGreater(length, 0)
        self.assertEqual(length, len(response.content))

    def test_query_http_auth_id_device(self):

        id_device = 1
        params = {
            'id_device': id_device
        }
        response = self._request_with_http_auth('participant1', 'opentera', params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        for item in json_data:
            self.assertEqual(id_device, item['id_device'])

    def test_query_http_auth_id_session(self):

        id_session = 1
        params = {
            'id_session': id_session
        }
        response = self._request_with_http_auth('participant1', 'opentera', params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        for item in json_data:
            self.assertEqual(id_session, item['id_session'])

    def test_query_http_auth_id_device_data(self):

        id_device_data = 1
        params = {
            'id_device_data': id_device_data
        }
        response = self._request_with_http_auth('participant1', 'opentera', params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        for item in json_data:
            self.assertEqual(id_device_data, item['id_device_data'])

