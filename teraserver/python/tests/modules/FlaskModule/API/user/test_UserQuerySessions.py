from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import datetime


class UserQuerySessionsTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/sessions'

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

    def test_query_list_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_session=1&list=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_session=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_for_participant_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_participant=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_for_user_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'session': {
                'session_name': 'Test Session',
                'session_start_datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                'id_session_type': 1,
                'session_status': 2
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_session")  # Missing id_session

        json_data['session']['id_session'] = 0
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing participants")  # Missing participants

        json_data['session']['session_participants_ids'] = [1, 2]
        response = self._post_with_http_auth(username='user4', password='user4', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

        json_data['session']['session_users_ids'] = [1]
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

        json_data = response.json()[0]
        self._checkJson(json_data)
        current_id = json_data['id_session']

        json_data = {
            'session': {
                'id_session': current_id,
                'session_status': 2,
                'session_name': 'Test Session 2'
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update")
        json_data = response.json()[0]
        self._checkJson(json_data)
        self.assertEqual(json_data['session_name'], 'Test Session 2')
        self.assertEqual(json_data['session_status'], 2)

        # Change participants
        json_data = {
            'session': {
                'id_session': current_id,
                'session_participants_ids': [2, 3]
            }
        }
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove participants")
        json_data = response.json()[0]
        self._checkJson(json_data)
        self.assertEqual(len(json_data['session_participants']), 2)
        # self.assertEqual(json_data['session_participants'][0]['id_participant'], 2)
        # self.assertEqual(json_data['session_participants'][1]['id_participant'], 3)

        response = self._delete_with_http_auth(username='user4', password='user4', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_session'))
        self.assertTrue(json_data.__contains__('id_creator_device'))
        self.assertTrue(json_data.__contains__('id_creator_participant'))
        self.assertTrue(json_data.__contains__('id_creator_service'))
        self.assertTrue(json_data.__contains__('id_creator_user'))
        self.assertTrue(json_data.__contains__('id_session_type'))
        self.assertTrue(json_data.__contains__('session_name'))
        self.assertTrue(json_data.__contains__('session_status'))
        self.assertTrue(json_data.__contains__('session_uuid'))

        if not minimal:
            self.assertTrue(json_data.__contains__('session_comments'))
            self.assertTrue(json_data.__contains__('session_duration'))
            self.assertTrue(json_data.__contains__('session_has_device_data'))
            self.assertTrue(json_data.__contains__('session_participants'))
            self.assertTrue(json_data.__contains__('session_users'))
            self.assertTrue(json_data.__contains__('session_start_datetime'))
