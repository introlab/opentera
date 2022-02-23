import os
import json
from datetime import datetime
from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
from opentera.services.ServiceOpenTera import ServiceOpenTera
from opentera.services.ServiceConfigManager import ServiceConfigManager


class ServiceAssetsTest(BaseAPITest):

    host = '127.0.0.1'
    port = 40075
    test_endpoint = '/api/service/assets'
    user_service_endpoint = '/api/user/services'
    service_token = None
    service_uuid = None

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
        self.service_uuid = services[0]['service_uuid']
        service_config.service_config['ServiceUUID'] = self.service_uuid
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
        self.assertEqual(401, response.status_code)

    def test_query_no_params(self):
        response = self._request_with_token_auth(token=self.service_token)
        self.assertEqual(400, response.status_code)

    def test_query_bad_params(self):
        params = {'id_invalid': 1}
        response = self._request_with_token_auth(token=self.service_token, payload=params)
        self.assertEqual(response.status_code, 400)

    def test_query_assets_by_service_uuid(self):
        payload = {'service_uuid': '00000000-0000-0000-0000-000000000001', 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertTrue(len(json_data), 4)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_device_assets(self):
        payload = {'id_device': 1, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertTrue(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_device_assets_no_access(self):
        payload = {'id_device': 4, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_session_assets(self):
        payload = {'id_session': 2}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 3)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_session_assets_no_access(self):
        payload = {'id_session': 100}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_participant_assets(self):
        payload = {'id_participant': 1, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertTrue(len(json_data), 4)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_participant_assets_no_access(self):
        payload = {'id_participant': 4, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_user_assets(self):
        payload = {'id_user': 1, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 4)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_user_assets_no_access(self):
        payload = {'id_user': 6, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_asset(self):
        payload = {'id_asset': 1, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertTrue(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_asset_no_access(self):
        payload = {'id_asset': 5, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)
        self.assertEqual(response.status_code, 200)

    def test_query_assets_created_by_service(self):
        payload = {'id_creator_service': 1, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertTrue(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_assets_created_by_user(self):
        payload = {'id_creator_user': 1, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertTrue(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_assets_created_by_user_no_access(self):
        payload = {'id_creator_user': 6, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_assets_created_by_participant(self):
        payload = {'id_creator_participant': 1, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertTrue(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_assets_created_by_participant_no_access(self):
        payload = {'id_creator_participant': 4, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_assets_created_by_device(self):
        payload = {'id_creator_device': 1, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertTrue(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_assets_created_by_device_no_access(self):
        payload = {'id_creator_device': 4, 'with_urls': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'asset': {
                'asset_name': 'Test Asset',
                'asset_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')            }
        }

        response = self._post_with_token(token=self.service_token, payload=json_data)
        self.assertEqual(400, response.status_code, msg="Missing id_asset")

        json_data['asset']['id_asset'] = 0
        response = self._post_with_token(token=self.service_token, payload=json_data)
        self.assertEqual(400, response.status_code, msg="Missing asset type")

        json_data['asset']['asset_type'] = 'application/octet-stream'

        response = self._post_with_token(token=self.service_token, payload=json_data)
        self.assertEqual(400, response.status_code, msg="Missing id_session")

        json_data['asset']['id_session'] = 2
        response = self._post_with_token(token=self.service_token, payload=json_data)
        self.assertEqual(200, response.status_code, msg="Post new")  # All ok now!

        json_data = response.json()[0]
        self._checkJson(json_data, minimal=True)
        current_id = json_data['id_asset']
        current_uuid = json_data['asset_uuid']

        json_data = {
            'asset': {
                'id_asset': current_id,
                'asset_service_uuid': '0000000000000',  # Bad service uuid - should be replaced in post reply
                'asset_name': 'Test Asset 2'
            }
        }

        response = self._post_with_token(token=self.service_token, payload=json_data)
        self.assertEqual(200, response.status_code, msg="Post update")
        json_data = response.json()[0]
        self._checkJson(json_data, minimal=True)
        self.assertEqual(json_data['asset_name'], 'Test Asset 2')
        self.assertEqual(json_data['asset_service_uuid'], self.service_uuid)

        # Delete
        response = self._delete_uuid_with_token(token=self.service_token, uuid_to_del=current_uuid)
        self.assertEqual(200, response.status_code, msg="Delete OK")

        # Bad delete
        response = self._delete_uuid_with_token(token=self.service_token, uuid_to_del=current_uuid)
        self.assertEqual(400, response.status_code, msg="Wrong delete")

    def test_query_session_assets_as_admin_token_only(self):
        payload = {'id_session': 2, 'with_urls': True, 'with_only_token': True}
        response = self._request_with_token_auth(token=self.service_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 3)
        for data_item in json_data:
            self.assertFalse(data_item.__contains__("asset_name"))
            self.assertTrue(data_item.__contains__("asset_uuid"))
            self.assertTrue(data_item.__contains__("access_token"))

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_asset'))
        self.assertTrue(json_data.__contains__('id_session'))
        self.assertTrue(json_data.__contains__('id_device'))
        self.assertTrue(json_data.__contains__('id_participant'))
        self.assertTrue(json_data.__contains__('id_user'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('asset_name'))
        self.assertTrue(json_data.__contains__('asset_uuid'))
        self.assertTrue(json_data.__contains__('asset_service_uuid'))
        self.assertTrue(json_data.__contains__('asset_type'))
        self.assertTrue(json_data.__contains__('asset_datetime'))
        if not minimal:
            self.assertTrue(json_data.__contains__('asset_infos_url'))
            self.assertTrue(json_data.__contains__('asset_url'))
            self.assertTrue(json_data.__contains__('access_token'))
