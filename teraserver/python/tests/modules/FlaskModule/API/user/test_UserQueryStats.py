from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest

import datetime


class UserQueryAssetsTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/stats'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_auth(self):
        response = self._request_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_query_no_params_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 400)

    def test_query_user_group_stats(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_user_group=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        response = self._request_with_http_auth(username='user4', password='user4', payload='id_user_group=1')
        self.assertEqual(response.status_code, 403)

    def test_query_user_stats(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_user=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        response = self._request_with_http_auth(username='user4', password='user4', payload='id_user=1')
        self.assertEqual(response.status_code, 403)

    def test_query_site_stats(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_site=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        response = self._request_with_http_auth(username='user4', password='user4', payload='id_site=1')
        self.assertEqual(response.status_code, 403)

    def test_query_project_stats(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_project=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        response = self._request_with_http_auth(username='user4', password='user4', payload='id_project=1')
        self.assertEqual(response.status_code, 403)

    def test_query_participant_group_stats(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_group=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        response = self._request_with_http_auth(username='user4', password='user4', payload='id_group=1')
        self.assertEqual(response.status_code, 403)

    def test_query_session_stats(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_session=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        response = self._request_with_http_auth(username='user4', password='user4', payload='id_session=1')
        self.assertEqual(response.status_code, 403)

    def test_query_participant_stats(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_participant=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        response = self._request_with_http_auth(username='user4', password='user4', payload='id_participant=1')
        self.assertEqual(response.status_code, 403)

    def test_query_device_stats(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_device=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        response = self._request_with_http_auth(username='user4', password='user4', payload='id_device=1')
        self.assertEqual(response.status_code, 403)