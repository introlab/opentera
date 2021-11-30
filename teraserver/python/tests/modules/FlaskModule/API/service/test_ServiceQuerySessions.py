import os
from requests import get, delete
import json
from datetime import datetime, timedelta
from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
from opentera.services.ServiceOpenTera import ServiceOpenTera
from opentera.services.ServiceConfigManager import ServiceConfigManager


class ServiceSessionsTest(BaseAPITest):

    host = '127.0.0.1'
    port = 40075
    test_endpoint = '/api/service/sessions'
    user_service_endpoint = '/api/user/services'
    user_session_endpoint = '/api/user/sessions'
    user_participant_endpoint = '/api/user/participants'
    service_token = None

    def setUp(self):
        # Initialize service from redis, posing as VideoRehabService
        # Use admin account to get service information (and tokens)
        response = self._request_with_http_auth(username='admin', password='admin', payload='key=VideoRehabService',
                                                endpoint=self.user_service_endpoint)
        self.assertEqual(response.status_code, 200)
        services = json.loads(response.text)
        self.assertEqual(len(services), 1)

        service_config = ServiceConfigManager()
        config_file = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) +
                                      '../../../../../../services/VideoRehabService/VideoRehabService.json')
        service_config.load_config(filename=config_file)
        service_config.service_config['ServiceUUID'] = services[0]['service_uuid']
        service = ServiceOpenTera(config_man=service_config, service_info=services[0])
        self.service_token = service.service_token

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
        self.assertEqual(405, response.status_code)  # Not implemented

    def test_query_no_params(self):
        response = self._request_with_token_auth(token=self.service_token)
        self.assertEqual(400, response.status_code)

    def test_query_list(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_session=1&list=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_session=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_specific_but_invalid(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_session=-1")
        self.assertEqual(403, response.status_code)

    def test_query_for_participant(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_participant=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            participant_count = 0
            for participant in data_item['session_participants']:
                participant_count += int(1 == participant['id_participant'])
            self.assertEqual(1, participant_count)

    def test_query_for_participant_with_list(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_participant=1&list=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_for_participant_with_limit(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_participant=1&limit=2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(2, len(json_data))

    def test_query_for_participant_with_limit_and_offset(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_participant=1&limit=2&offset=27")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

    def test_query_for_participant_with_status(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_participant=1&status=0")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(12, len(json_data))

        for data_item in json_data:
            self.assertEqual(0, data_item['session_status'])

    def test_query_for_participant_with_limit_and_offset_and_status_and_list(self):
        response = self._request_with_token_auth(token=self.service_token,
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
        response = self._request_with_token_auth(token=self.service_token,
                                                 payload="id_participant=1&start_date=" + start_date +
                                                         "&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(6, len(json_data))

    def test_query_for_participant_with_start_date(self):
        start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
        response = self._request_with_token_auth(token=self.service_token,
                                                 payload="id_participant=1&start_date=" + start_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(12, len(json_data))

    def test_query_for_participant_with_end_date(self):
        end_date = (datetime.now() - timedelta(days=5)).date().strftime("%Y-%m-%d")
        response = self._request_with_token_auth(token=self.service_token,
                                                 payload="id_participant=1&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(9, len(json_data))

    def test_query_for_not_accessible_user(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_user=6")
        self.assertEqual(403, response.status_code)

    def test_query_for_not_accessible_participant(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_participant=4")
        self.assertEqual(403, response.status_code)

    def test_query_for_not_accessible_device(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_device=3")
        self.assertEqual(403, response.status_code)

    def test_query_for_user(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_user=3")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            user_count = 0
            for user in data_item['session_users']:
                user_count += int(3 == user['id_user'])
            self.assertEqual(1, user_count)

    def test_query_for_user_with_list(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_user=3&list=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_for_user_with_limit(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_user=3&limit=2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(2, len(json_data))

    def test_query_for_user_with_limit_and_offset(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_user=3&limit=2&offset=4")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

    def test_query_for_user_with_status(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_user=3&status=2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(2, len(json_data))

        for data_item in json_data:
            self.assertEqual(2, data_item['session_status'])

    def test_query_for_user_with_limit_and_offset_and_status_and_list(self):
        response = self._request_with_token_auth(token=self.service_token,
                                                 payload="id_user=3&list=1&limit=2&offset=1&status=2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

        for data_item in json_data:
            self.assertEqual(2, data_item['session_status'])

    def test_query_for_user_with_start_date_and_end_date(self):
        start_date = (datetime.now() - timedelta(days=6)).date().strftime("%Y-%m-%d")
        end_date = (datetime.now() - timedelta(days=4)).date().strftime("%Y-%m-%d")
        response = self._request_with_token_auth(token=self.service_token,
                                                 payload="id_user=3&start_date=" + start_date +
                                                         "&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(2, len(json_data))

    def test_query_for_user_with_start_date(self):
        start_date = (datetime.now() - timedelta(days=6)).date().strftime("%Y-%m-%d")
        response = self._request_with_token_auth(token=self.service_token,
                                                 payload="id_user=3&start_date=" + start_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(3, len(json_data))

    def test_query_for_user_with_end_date(self):
        end_date = (datetime.now() - timedelta(days=4)).date().strftime("%Y-%m-%d")
        response = self._request_with_token_auth(token=self.service_token,
                                                 payload="id_user=3&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(4, len(json_data))

    def test_query_for_device(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_device=2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        for data_item in json_data:
            self._checkJson(json_data=data_item)
            device_count = 0
            for device in data_item['session_devices']:
                device_count += int(2 == device['id_device'])
            self.assertEqual(1, device_count)

    def test_query_for_device_with_list(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_device=2&list=1")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_for_device_with_limit(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_device=1&limit=2")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(2, len(json_data))

    def test_query_for_device_with_limit_and_offset(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_device=1&limit=2&offset=7")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

    def test_query_for_device_with_status(self):
        response = self._request_with_token_auth(token=self.service_token, payload="id_device=1&status=0")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(3, len(json_data))

        for data_item in json_data:
            self.assertEqual(0, data_item['session_status'])

    def test_query_for_device_with_limit_and_offset_and_status_and_list(self):
        response = self._request_with_token_auth(token=self.service_token,
                                                 payload="id_device=1&list=1&limit=2&offset=2&status=0")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(1, len(json_data))

        for data_item in json_data:
            self.assertEqual(0, data_item['session_status'])

    def test_query_for_device_with_limit_and_list_and_start_date_and_end_date(self):
        start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
        end_date = (datetime.now() - timedelta(days=1)).date().strftime("%Y-%m-%d")
        response = self._request_with_token_auth(token=self.service_token,
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
        response = self._request_with_token_auth(token=self.service_token,
                                                 payload="id_device=1&start_date=" + start_date +
                                                         "&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(2, len(json_data))

    def test_query_for_device_with_start_date(self):
        start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
        response = self._request_with_token_auth(token=self.service_token,
                                                 payload="id_device=1&start_date=" + start_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(3, len(json_data))

    def test_query_for_device_with_end_date(self):
        end_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
        response = self._request_with_token_auth(token=self.service_token,
                                                 payload="id_device=1&end_date=" + end_date)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        self.assertEqual(5, len(json_data))

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'session': {
                'session_name': 'Test Session',
                'session_start_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                'id_session_type': 1,
                'session_status': 2
            }
        }

        response = self._post_with_token(token=self.service_token, payload=json_data)
        self.assertEqual(400, response.status_code, msg="Missing id_session")  # Missing id_session

        json_data['session']['id_session'] = 0
        # response = self._post_with_token(token=self.service_token, payload=json_data)
        # self.assertEqual(400, response.status_code, msg="Missing participants")  # Missing participants

        # Get participants uuids
        url = self._make_url(self.host, self.port, self.user_participant_endpoint)
        response = get(url=url, verify=False, auth=('admin', 'admin'), params='id_participant=1')
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))
        p1_uuid = response.json()[0]['participant_uuid']

        url = self._make_url(self.host, self.port, self.user_participant_endpoint)
        response = get(url=url, verify=False, auth=('admin', 'admin'), params='id_participant=2')
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))
        p2_uuid = response.json()[0]['participant_uuid']

        url = self._make_url(self.host, self.port, self.user_participant_endpoint)
        response = get(url=url, verify=False, auth=('admin', 'admin'), params='id_participant=4')
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))
        p4_uuid = response.json()[0]['participant_uuid']

        json_data['session']['session_participants_uuids'] = [p1_uuid, p4_uuid]
        response = self._post_with_token(token=self.service_token, payload=json_data)
        self.assertEqual(403, response.status_code, msg="Post denied for user")  # Forbidden for that user to post that

        # json_data['session']['session_users_ids'] = [1]
        json_data['session']['session_participants_uuids'] = [p1_uuid, p2_uuid]
        response = self._post_with_token(token=self.service_token, payload=json_data)
        self.assertEqual(200, response.status_code, msg="Post new")  # All ok now!

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

        response = self._post_with_token(token=self.service_token, payload=json_data)
        self.assertEqual(200, response.status_code, msg="Post update")
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
        response = self._post_with_token(token=self.service_token, payload=json_data)
        self.assertEqual(200, response.status_code, msg="Remove participants")
        json_data = response.json()[0]
        self._checkJson(json_data)
        self.assertEqual(len(json_data['session_participants']), 2)
        # self.assertEqual(json_data['session_participants'][0]['id_participant'], 2)
        # self.assertEqual(json_data['session_participants'][1]['id_participant'], 3)

        url = self._make_url(self.host, self.port, self.user_session_endpoint)
        response = delete(url=url, verify=False, auth=('admin', 'admin'), params='id=' + str(current_id))
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
