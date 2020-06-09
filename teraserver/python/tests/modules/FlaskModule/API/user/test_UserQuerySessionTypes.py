import unittest
from requests import get, post, delete
import json


class UserQuerySessionTypesTest(unittest.TestCase):
    host = 'localhost'
    port = 40075
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/sessiontypes'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _make_url(self, hostname, port, endpoint):
        return 'https://' + hostname + ':' + str(port) + endpoint

    def _request_with_http_auth(self, username, password, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return get(url=url, verify=False, auth=(username, password), params=payload)

    def _request_with_no_auth(self, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return get(url=url, verify=False, params=payload)

    def _post_with_http_auth(self, username, password, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return post(url=url, verify=False, auth=(username, password), json=payload)

    def _post_with_no_auth(self, payload=None):
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return post(url=url, verify=False, json=payload)

    def _delete_with_http_auth(self, username, password, id_to_del: int):
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return delete(url=url, verify=False, auth=(username, password), params='id=' + str(id_to_del))

    def _delete_with_no_auth(self, id_to_del: int):
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return delete(url=url, verify=False, params='id=' + str(id_to_del))

    def test_no_auth(self):
        response = self._request_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_post_no_auth(self):
        response = self._post_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_delete_no_auth(self):
        response = self._delete_with_no_auth(id_to_del=0)
        self.assertEqual(response.status_code, 401)

    def test_query_no_params_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        for data_item in json_data:
            self.assertGreater(len(data_item), 0)
            self.assertTrue(data_item.__contains__('id_session_type'))
            self.assertTrue(data_item.__contains__('session_type_category'))
            self.assertTrue(data_item.__contains__('session_type_config'))
            self.assertTrue(data_item.__contains__('session_type_multi'))
            self.assertTrue(data_item.__contains__('session_type_name'))
            self.assertTrue(data_item.__contains__('session_type_online'))
            self.assertTrue(data_item.__contains__('session_type_color'))

    def test_query_list_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="list=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_session_type=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'session_type': {
                'id_service': None,
                'session_type_category': 1,
                'session_type_color': 'red',
                'session_type_multi': False,
                'session_type_name': 'Test',
                'session_type_online': True
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_session_type")  # Missing id_session_type

        json_data['session_type']['id_session_type'] = 0
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_service")  # Missing id_service

        json_data['session_type']['id_service'] = 1
        response = self._post_with_http_auth(username='user4', password='user4', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

        json_data = response.json()[0]
        self._checkJson(json_data)
        current_id = json_data['id_session_type']

        json_data = {
            'session_type': {
                'id_session_type': current_id,
                'session_type_category': 2,
                'session_type_name': 'Test 2'
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update")
        json_data = response.json()[0]
        self._checkJson(json_data)
        self.assertEqual(json_data['session_type_name'], 'Test 2')
        self.assertEqual(json_data['session_type_category'], 2)

        response = self._delete_with_http_auth(username='user4', password='user4', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_session_type'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('session_type_category'))
        self.assertTrue(json_data.__contains__('session_type_name'))
        if not minimal:
            self.assertTrue(json_data.__contains__('session_type_config'))
            self.assertTrue(json_data.__contains__('session_type_multi'))
            self.assertTrue(json_data.__contains__('session_type_online'))
            self.assertTrue(json_data.__contains__('session_type_color'))

