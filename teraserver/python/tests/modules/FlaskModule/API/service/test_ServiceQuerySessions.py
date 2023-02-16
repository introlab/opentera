from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from datetime import datetime, timedelta
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraParticipant import TeraParticipant


class ServiceQuerySessionsTest(BaseServiceAPITest):
    test_endpoint = '/api/service/sessions'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_with_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_with_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_no_auth(self):
        with self._flask_app.app_context():
            params = {'id_session': 0}
            response = self.test_client.delete(self.test_endpoint, query_string=params)
            self.assertEqual(405, response.status_code)  # Not implemented

    def test_get_endpoint_query_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_query_list(self):
        with self._flask_app.app_context():
            params = {'id_session': 1, 'list': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)

            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertGreater(len(response.json), 0)

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_get_endpoint_query_specific(self):
        with self._flask_app.app_context():
            params = {'id_session': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)

            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_get_endpoint_query_specific_but_invalid(self):
        with self._flask_app.app_context():
            params = {'id_session': -1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_query_for_participant(self):
        with self._flask_app.app_context():
            params = {'id_participant': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                participant_count = 0
                for participant in data_item['session_participants']:
                    participant_count += int(1 == participant['id_participant'])
                self.assertEqual(1, participant_count)

    def test_get_endpoint_query_for_participant_with_list(self):
        with self._flask_app.app_context():
            params = {'id_participant': 1, 'list': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_get_endpoint_query_for_participant_with_limit(self):
        with self._flask_app.app_context():
            params = {'id_participant': 1, 'limit': 2}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(2, len(response.json))

    def test_get_endpoint_query_for_participant_with_limit_and_offset(self):
        with self._flask_app.app_context():
            params = {'id_participant': 1, 'limit': 2, 'offset': 27}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)

            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(1, len(response.json))

    def test_get_endpoint_query_for_participant_with_status(self):
        with self._flask_app.app_context():
            params = {'id_participant': 1, 'status': 0}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(12, len(response.json))

            for data_item in response.json:
                self.assertEqual(0, data_item['session_status'])

    def test_get_endpoint_query_for_participant_with_limit_and_offset_and_status_and_list(self):
        with self._flask_app.app_context():
            params = {'id_participant': 1, 'list': 1, 'limit': 2, 'offset': 11, 'status': 0}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self.assertEqual(0, data_item['session_status'])

    def test_get_endpoint_query_for_participant_with_start_date_and_end_date(self):
        with self._flask_app.app_context():
            start_date = (datetime.now() - timedelta(days=6)).date().strftime("%Y-%m-%d")
            end_date = (datetime.now() - timedelta(days=4)).date().strftime("%Y-%m-%d")
            params = {'id_participant': 1, 'start_date': start_date, 'end_date': end_date}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(6, len(response.json))

    def test_get_endpoint_query_for_participant_with_start_date(self):
        with self._flask_app.app_context():
            start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
            params = {'id_participant': 1, 'start_date': start_date}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(12, len(response.json))

    def test_get_endpoint_query_for_participant_with_end_date(self):
        with self._flask_app.app_context():
            end_date = (datetime.now() - timedelta(days=5)).date().strftime("%Y-%m-%d")
            params = {'id_participant': 1, 'end_date': end_date}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(9, len(response.json))

    def test_get_endpoint_query_for_not_accessible_user(self):
        with self._flask_app.app_context():
            params = {'id_user': 6}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_query_for_not_accessible_participant(self):
        with self._flask_app.app_context():
            params = {'id_participant': 4}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_query_for_not_accessible_device(self):
        with self._flask_app.app_context():
            params = {'id_device': 3}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_query_for_user(self):
        with self._flask_app.app_context():
            params = {'id_user': 3}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                user_count = 0
                for user in data_item['session_users']:
                    user_count += int(3 == user['id_user'])
                self.assertEqual(1, user_count)

    def test_get_endpoint_query_for_user_with_list(self):
        with self._flask_app.app_context():
            params = {'id_user': 3, 'list': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_get_endpoint_query_for_user_with_limit(self):
        with self._flask_app.app_context():
            params = {'id_user': 3, 'limit': 2}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(2, len(response.json))

    def test_get_endpoint_query_for_user_with_limit_and_offset(self):
        with self._flask_app.app_context():
            params = {'id_user': 3, 'limit': 2, 'offset': 4}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(1, len(response.json))

    def test_get_endpoint_query_for_user_with_status(self):
        with self._flask_app.app_context():
            params = {'id_user': 3, 'status': 2}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self.assertEqual(2, data_item['session_status'])

    def test_get_endpoint_query_for_user_with_limit_and_offset_and_status_and_list(self):
        with self._flask_app.app_context():
            params = {'id_user': 3, 'list': 1, 'limit': 2, 'offset': 1, 'status': 2}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)

            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self.assertEqual(2, data_item['session_status'])

    def test_get_endpoint_query_for_user_with_start_date_and_end_date(self):
        with self._flask_app.app_context():
            start_date = (datetime.now() - timedelta(days=6)).date().strftime("%Y-%m-%d")
            end_date = (datetime.now() - timedelta(days=4)).date().strftime("%Y-%m-%d")

            params = {'id_user': 3, 'start_date': start_date, 'end_date': end_date}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(2, len(response.json))

    def test_get_endpoint_query_for_user_with_start_date(self):
        with self._flask_app.app_context():
            start_date = (datetime.now() - timedelta(days=6)).date().strftime("%Y-%m-%d")

            params = {'id_user': 3, 'start_date': start_date}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(3, len(response.json))

    def test_get_endpoint_query_for_user_with_end_date(self):
        with self._flask_app.app_context():
            end_date = (datetime.now() - timedelta(days=4)).date().strftime("%Y-%m-%d")

            params = {'id_user': 3, 'end_date': end_date}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(4, len(response.json))

    def test_get_endpoint_query_for_device(self):
        with self._flask_app.app_context():
            params = {'id_device': 2}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            for data_item in response.json:
                self._checkJson(json_data=data_item)
                device_count = 0
                for device in data_item['session_devices']:
                    device_count += int(2 == device['id_device'])
                self.assertEqual(1, device_count)

    def test_get_endpoint_query_for_device_with_list(self):
        with self._flask_app.app_context():
            params = {'id_device': 2, 'list': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_get_endpoint_query_for_device_with_limit(self):
        with self._flask_app.app_context():
            params = {'id_device': 1, 'limit': 2}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(2, len(response.json))

    def test_get_endpoint_query_for_device_with_limit_and_offset(self):
        with self._flask_app.app_context():
            params = {'id_device': 1, 'limit': 2, 'offset': 7}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            count = len(TeraSession.get_sessions_for_device(device_id=1, limit=2, offset=7))
            self.assertEqual(count, len(response.json))

    def test_get_endpoint_query_for_device_with_status(self):
        with self._flask_app.app_context():
            params = {'id_device': 1, 'status': 0}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            count = len(TeraSession.get_sessions_for_device(device_id=1, status=0))
            self.assertEqual(count, len(response.json))

            for data_item in response.json:
                self.assertEqual(0, data_item['session_status'])

    def test_get_endpoint_query_for_device_with_limit_and_offset_and_status_and_list(self):
        with self._flask_app.app_context():
            params = {'id_device': 1, 'list': 1, 'limit': 2, 'offset': 2, 'status': 0}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            count = len(TeraSession.get_sessions_for_device(device_id=1, limit=2,
                                                            offset=2, status=0))
            self.assertEqual(count, len(response.json))

            for data_item in response.json:
                self.assertEqual(0, data_item['session_status'])

    def test_get_endpoint_query_for_device_with_limit_and_list_and_start_date_and_end_date(self):
        with self._flask_app.app_context():
            start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
            end_date = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
            params = {'id_device': 1, 'list': 1, 'limit': 1, 'start_date': start_date, 'end_date': end_date}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self.assertEqual(0, data_item['session_status'])

    def test_get_endpoint_query_for_device_with_start_date_and_end_date(self):
        with self._flask_app.app_context():
            start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
            end_date = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
            params = {'id_device': 1, 'start_date': start_date, 'end_date': end_date}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            count = len(TeraSession.get_sessions_for_device(device_id=1, start_date=datetime.fromisoformat(start_date),
                                                            end_date=datetime.fromisoformat(end_date)))
            self.assertEqual(count, len(response.json))

    def test_get_endpoint_query_for_device_with_start_date(self):
        with self._flask_app.app_context():
            start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
            params = {'id_device': 1, 'start_date': start_date}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            count = len(TeraSession.get_sessions_for_device(device_id=1, start_date=datetime.fromisoformat(start_date)))
            self.assertEqual(count, len(response.json))

    def test_get_endpoint_query_for_device_with_end_date(self):
        with self._flask_app.app_context():
            end_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
            params = {'id_device': 1, 'end_date': end_date}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.headers['Content-Type'], 'application/json')

            count = len(TeraSession.get_sessions_for_device(device_id=1, end_date=datetime.fromisoformat(end_date)))
            self.assertEqual(count, len(response.json))

    def test_post_and_delete_endpoint(self):
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

            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, endpoint=self.test_endpoint)

            self.assertEqual(400, response.status_code, msg="Missing id_session")  # Missing id_session

            json_data['session']['id_session'] = 0  # New session

            # Get participants uuids
            p1_uuid = TeraParticipant.get_participant_by_id(1).participant_uuid
            p2_uuid = TeraParticipant.get_participant_by_id(2).participant_uuid
            p3_uuid = TeraParticipant.get_participant_by_id(3).participant_uuid
            p4_uuid = TeraParticipant.get_participant_by_id(4).participant_uuid

            # Set Participants
            json_data['session']['session_participants_uuids'] = [p1_uuid, p4_uuid]
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, endpoint=self.test_endpoint)

            # Forbidden for that user to post that
            self.assertEqual(403, response.status_code, msg="Post denied for user")

            json_data['session']['session_participants_uuids'] = [p1_uuid, p2_uuid]
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, endpoint=self.test_endpoint)
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

            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg="Post update")
            json_data = response.json[0]
            self._checkJson(json_data)
            self.assertEqual(json_data['session_name'], 'Test Session 2')
            self.assertEqual(json_data['session_status'], 2)

            # Change participants
            json_data = {
                'session': {
                    'id_session': current_id,
                    'session_participants_uuids': [p2_uuid, p3_uuid]
                }
            }

            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg="Remove participants")
            json_data = response.json[0]
            self._checkJson(json_data)
            self.assertEqual(len(json_data['session_participants']), 2)

            # TODO use delete endpoint ?
            # Delete session
            from opentera.db.models.TeraSession import TeraSession
            TeraSession.delete(current_id)
            self.assertIsNone(TeraSession.get_session_by_id(current_id))

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
            self.assertTrue(json_data.__contains__('session_participants'))
            self.assertTrue(json_data.__contains__('session_users'))
            self.assertTrue(json_data.__contains__('session_start_datetime'))
