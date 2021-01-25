from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import datetime


class UserQueryServiceAccessTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/services/access'

    def setUp(self):
        pass

    def tearDown(self):
        pass

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
        self.assertEqual(response.status_code, 400)

    def test_query_for_service(self):
        response = self._request_with_http_auth(username='user4', password='user4', payload="id_service=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_service=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_service'], 4)

    def test_query_for_user_group(self):
        response = self._request_with_http_auth(username='user4', password='user4', payload="id_user_group=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user_group=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user_group'], 2)
            self.assertTrue(data_item.__contains__('user_group_name'))

    def test_query_for_device(self):
        response = self._request_with_http_auth(username='user4', password='user4', payload="id_device=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_device=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_device'], 1)
            self.assertTrue(data_item.__contains__('device_name'))

    def test_query_for_participant_group(self):
        response = self._request_with_http_auth(username='user4', password='user4', payload="id_participant_group=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_participant_group=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_participant_group'], 1)
            self.assertTrue(data_item.__contains__('participant_group_name'))

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'service_access': {
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_service_access")

        json_data['service_access']['id_service_access'] = 0
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing at least one id field")

        json_data['service_access']['id_user_group'] = 1
        json_data['service_access']['id_device'] = 1
        json_data['service_access']['id_participant_group'] = 1
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Cant combine ids")

        del json_data['service_access']['id_device']
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Cant combine ids")

        del json_data['service_access']['id_participant_group']
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_service_role")

        json_data['service_access']['id_service_role'] = 5
        response = self._post_with_http_auth(username='user4', password='user4', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

        json_data = response.json()[0]
        current_id = json_data['id_service_access']

        json_data = {
            'service_access': {
                'id_service_access': current_id
            }
        }
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Deleted access")
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        json_data = {
            'service_access': {
                'id_service_access': 0,
                'id_service_role': 5,
                'id_participant_group': 1
            }
        }
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok

        json_data = response.json()[0]
        self.assertEqual(json_data['id_service_role'], 5)
        self.assertEqual(json_data['id_participant_group'], 1)

        current_id = json_data['id_service_access']

        json_data = {
            'service_access': {
                'id_service_access': current_id,
                'id_service_role': 6
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update OK")
        json_data = response.json()[0]
        self.assertEqual(json_data['id_service_role'], 6)

        response = self._delete_with_http_auth(username='user4', password='user4', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertTrue(json_data.__contains__('id_service_access'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('id_service_role'))
        self.assertTrue(json_data.__contains__('service_role_name'))
        self.assertTrue(json_data.__contains__('service_name'))
