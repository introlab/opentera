from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from datetime import datetime, timedelta


class UserQuerySessionsTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/sessions'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_auth(self):
        response = self._request_with_no_auth()
        self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        response = self._post_with_no_auth()
        self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        response = self._delete_with_no_auth(id_to_del=0)
        self.assertEqual(401, response.status_code)

    def test_query_no_params_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin')
        self.assertEqual(400, response.status_code)

    def test_query_list_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_session=1&list=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_session=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_specific_but_invalid_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_session=-1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

    def test_query_for_participant_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_participant=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            participant_count = 0
            for participant in data_item['session_participants']:
                participant_count += int(1 == participant['id_participant'])
            self.assertEqual(1, participant_count)

    def test_query_for_participant_as_admin_with_list(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_participant=1&list=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_for_participant_as_admin_with_limit(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_participant=1&limit=2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(2, len(json_data))

    def test_query_for_participant_as_admin_with_limit_and_offset(self):
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_participant=1&limit=2&offset=27")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

    def test_query_for_participant_as_admin_with_status(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_participant=1&status=0")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(12, len(json_data))

        for data_item in json_data:
            self.assertEqual(0, data_item['session_status'])

    def test_query_for_participant_as_admin_with_limit_and_offset_and_status_and_list(self):
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_participant=1&list=1&limit=2&offset=11&status=0")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

        for data_item in json_data:
            self.assertEqual(0, data_item['session_status'])

    def test_query_for_participant_with_start_date_and_end_date(self):
        start_date = (datetime.now() - timedelta(days=6)).date().strftime("%Y-%m-%d")
        end_date = (datetime.now() - timedelta(days=4)).date().strftime("%Y-%m-%d")
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_participant=1&start_date=" + start_date +
                                                        "&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(6, len(json_data))

    def test_query_for_participant_with_start_date(self):
        start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_participant=1&start_date=" + start_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(12, len(json_data))

    def test_query_for_participant_with_end_date(self):
        end_date = (datetime.now() - timedelta(days=5)).date().strftime("%Y-%m-%d")
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_participant=1&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(9, len(json_data))

    def test_query_for_participant_with_session_type(self):
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_participant=1&with_session_type=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(28, len(json_data))
        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('session_type_name'))
            self.assertTrue(data_item.__contains__('session_type_color'))

    def test_query_for_user_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            user_count = 0
            for user in data_item['session_users']:
                user_count += int(2 == user['id_user'])
            self.assertEqual(1, user_count)

    def test_query_for_user_as_admin_with_list(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=2&list=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_for_user_as_admin_with_limit(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=1&limit=2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(2, len(json_data))

    def test_query_for_user_as_admin_with_limit_and_offset(self):
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_user=1&limit=2&offset=7")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

    def test_query_for_user_as_admin_with_status(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=1&status=0")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(3, len(json_data))

        for data_item in json_data:
            self.assertEqual(0, data_item['session_status'])

    def test_query_for_user_as_admin_with_limit_and_offset_and_status_and_list(self):
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_user=1&list=1&limit=2&offset=2&status=0")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

        for data_item in json_data:
            self.assertEqual(0, data_item['session_status'])

    def test_query_for_user_with_start_date_and_end_date(self):
        start_date = (datetime.now() - timedelta(days=6)).date().strftime("%Y-%m-%d")
        end_date = (datetime.now() - timedelta(days=4)).date().strftime("%Y-%m-%d")
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_user=3&start_date=" + start_date +
                                                        "&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(2, len(json_data))

    def test_query_for_user_with_start_date(self):
        start_date = (datetime.now() - timedelta(days=6)).date().strftime("%Y-%m-%d")
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_user=3&start_date=" + start_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(3, len(json_data))

    def test_query_for_user_with_end_date(self):
        end_date = (datetime.now() - timedelta(days=4)).date().strftime("%Y-%m-%d")
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_user=3&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(4, len(json_data))

    def test_query_for_device_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_device=2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        for data_item in json_data:
            self._checkJson(json_data=data_item)
            device_count = 0
            for device in data_item['session_devices']:
                device_count += int(2 == device['id_device'])
            self.assertEqual(1, device_count)

    def test_query_for_device_as_admin_with_list(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_device=2&list=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_for_device_as_admin_with_limit(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_device=1&limit=2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(2, len(json_data))

    def test_query_for_device_as_admin_with_limit_and_offset(self):
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_device=1&limit=2&offset=11")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

    def test_query_for_device_as_admin_with_status(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_device=1&status=0")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(6, len(json_data))

        for data_item in json_data:
            self.assertEqual(0, data_item['session_status'])

    def test_query_for_device_as_admin_with_limit_and_offset_and_status_and_list(self):
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_device=1&list=1&limit=2&offset=5&status=0")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

        for data_item in json_data:
            self.assertEqual(0, data_item['session_status'])

    def test_query_for_device_with_limit_and_list_and_start_date_and_end_date(self):
        start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
        end_date = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_device=1&list=1&limit=1&start_date=" + start_date +
                                                "&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

        for data_item in json_data:
            self.assertEqual(0, data_item['session_status'])

    def test_query_for_device_with_start_date_and_end_date(self):
        start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
        end_date = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_device=1&start_date=" + start_date +
                                                "&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(4, len(json_data))

    def test_query_for_device_with_start_date(self):
        start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_device=1&start_date=" + start_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(6, len(json_data))

    def test_query_for_device_with_end_date(self):
        end_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_device=1&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(6, len(json_data))

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
            # self.assertTrue(json_data.__contains__('session_has_device_data'))
            self.assertTrue(json_data.__contains__('session_participants'))
            self.assertTrue(json_data.__contains__('session_users'))
            self.assertTrue(json_data.__contains__('session_start_datetime'))
            self.assertTrue(json_data.__contains__('session_parameters'))


class TeraSessionPostTest(BaseUserAPITest):

    test_endpoint = '/api/user/sessions'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {
                'session': {
                    'session_name': 'Test Session',
                    'session_start_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                    'id_session_type': 1,
                    'session_status': 2
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)

            self.assertEqual(400, response.status_code, msg="Missing id_session")  # Missing id_session

            json_data['session']['id_session'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing participants")  # Missing participants

            json_data['session']['session_participants_ids'] = [1, 2]
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)

            self.assertEqual(403, response.status_code, msg="Post denied for user")

            json_data['session']['session_users_ids'] = [1]
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post new")  # All ok now!

            json_data = response.json[0]
            self._checkJson(json_data)
            current_id = json_data['id_session']

            json_data = {
                'session': {
                    'id_session': current_id,
                    'session_status': 2,
                    'session_name': 'Test Session 2'
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post update")
            json_data = response.json[0]
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
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove participants")
            json_data = response.json[0]
            self._checkJson(json_data)
            self.assertEqual(len(json_data['session_participants']), 2)
            # self.assertEqual(json_data['session_participants'][0]['id_participant'], 2)
            # self.assertEqual(json_data['session_participants'][1]['id_participant'], 3)

            # Add parameters
            json_data = {
                'session': {
                    'id_session': current_id,
                    'session_parameters': 'ParametersXYZJSONString'
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Adding Parameters")
            response_data = response.json[0]
            self._checkJson(response_data)
            self.assertEqual(json_data['session']['session_parameters'], response_data['session_parameters'])

            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params={'id': current_id})
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(200, response.status_code, msg="Delete OK")

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
            # self.assertTrue(json_data.__contains__('session_has_device_data'))
            self.assertTrue(json_data.__contains__('session_participants'))
            self.assertTrue(json_data.__contains__('session_users'))
            self.assertTrue(json_data.__contains__('session_start_datetime'))
            self.assertTrue(json_data.__contains__('session_parameters'))


# TODO Test with inaccessible sessions, participants, users, devices...

