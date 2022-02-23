from requests import get
import json
from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest


class ParticipantQueryAssetsTest(BaseAPITest):
    login_endpoint = '/api/participant/login'
    test_endpoint = '/api/participant/assets'
    participant_static_token = None
    participant_dynamic_token = None

    def setUp(self):
        # Get participant static token
        params = {'id_participant': 1}
        response = self._request_with_http_auth('admin', 'admin', params, '/api/user/participants')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data[0].__contains__('participant_token'))
        self.participant_static_token = json_data[0]['participant_token']

        # Get participant dynamic token
        params = {}
        response = self._request_with_http_auth('participant1', 'opentera', params, '/api/participant/login')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data.__contains__('participant_token'))
        self.participant_dynamic_token = json_data['participant_token']

    def tearDown(self):
        pass

    def test_no_auth(self):
        response = self._request_with_no_auth()
        self.assertEqual(401, response.status_code)

    def test_static_token(self):
        response = self._request_with_token_auth(self.participant_static_token, 'id_asset=1&with_urls=True')
        self.assertEqual(response.status_code, 403)

    def test_query_assets_get_id(self):
        response = self._request_with_token_auth(self.participant_dynamic_token, 'id_asset=1&with_urls=True')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(len(json_data), 1)
        self._checkJson(json_data=json_data[0])

    def test_query_assets_get_id_forbidden(self):
        response = self._request_with_token_auth(self.participant_dynamic_token, 'id_asset=2')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

    def test_query_assets_get_uuid(self):
        response = self._request_with_token_auth(self.participant_dynamic_token, 'id_asset=1')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        asset_uuid = json_data[0]['asset_uuid']
        response = self._request_with_token_auth(self.participant_dynamic_token, 'asset_uuid=' + asset_uuid)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        self._checkJson(json_data=json_data[0], minimal=True)

    def test_query_assets_get_uuid_forbidden(self):
        params = {'id_asset': 2}
        response = self._request_with_http_auth('admin', 'admin', params, '/api/user/assets')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        self.assertTrue(json_data[0].__contains__('asset_uuid'))
        asset_uuid = json_data[0]['asset_uuid']
        response = self._request_with_token_auth(self.participant_dynamic_token, 'asset_uuid=' + asset_uuid)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

    def test_query_assets_all(self):
        response = self._request_with_token_auth(self.participant_dynamic_token)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        for asset_info in json_data:
            self._checkJson(json_data=asset_info, minimal=True)

    def test_query_assets_all_token_only(self):
        payload = {'with_only_token': True}
        response = self._request_with_token_auth(token=self.participant_dynamic_token, payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 1)
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
