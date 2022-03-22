from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from datetime import datetime


class ServiceQueryAssetsTest(BaseServiceAPITest):
    test_endpoint = '/api/service/assets'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import service_api_ns
        from BaseServiceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.service.ServiceQueryAssets import ServiceQueryAssets
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseServiceAPITest.getConfig())}
        service_api_ns.add_resource(ServiceQueryAssets, '/assets', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        response = self.test_client.get(self.test_endpoint)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=None, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code)

    def test_post_endpoint_no_auth(self):
        response = self.test_client.post(self.test_endpoint)
        self.assertEqual(401, response.status_code)

    def test_delete_endpoint_no_auth(self):
        params = {'uuid': 0}
        response = self.test_client.delete(self.test_endpoint, query_string=params)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_query_no_params(self):
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=None, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code)

    def test_get_endpoint_query_bad_params(self):
        params = {'id_invalid': 1}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 400)

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

    def test_get_endpoint_query_assets_by_service_uuid(self):
        params = {'service_uuid': '00000000-0000-0000-0000-000000000001', 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json), 4)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_device_assets(self):
        params = {'id_device': 1, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json), 1)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_device_assets_no_access(self):
        params = {'id_device': 4, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_endpoint_query_device_assets_no_access(self):
        params = {'id_device': 4, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_endpoint_query_session_assets(self):
        params = {'id_session': 2}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)

        for data_item in response.json:
            self._checkJson(json_data=data_item, minimal=True)

    def test_get_endpoint_query_session_assets_no_access(self):
        params = {'id_session': 100}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_endpoint_query_participant_assets(self):
        params = {'id_participant': 1, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json), 4)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_participant_assets_no_access(self):
        params = {'id_participant': 4, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_endpoint_query_user_assets(self):
        params = {'id_user': 1, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 4)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_user_assets_no_access(self):
        params = {'id_user': 6, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_endpoint_query_asset(self):
        params = {'id_asset': 1, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json), 1)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_asset_no_access(self):
        params = {'id_asset': 5, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)


    def test_get_endpoint_query_assets_created_by_service(self):
        params = {'id_creator_service': 1, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json), 1)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_assets_created_by_user(self):
        params = {'id_creator_user': 1, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json), 1)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_assets_created_by_user_no_access(self):
        params = {'id_creator_user': 6, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_endpoint_query_assets_created_by_participant(self):
        params = {'id_creator_participant': 1, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json), 1)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_assets_created_by_participant_no_access(self):
        params = {'id_creator_participant': 4, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_endpoint_query_assets_created_by_device(self):
        params = {'id_creator_device': 1, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json), 1)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_assets_created_by_device_no_access(self):
        params = {'id_creator_device': 4, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_update_and_delete(self):
        # New with minimal infos
        json_data = {
            'asset': {
                'asset_name': 'Test Asset',
                'asset_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')            }
        }

        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=json_data, endpoint=self.test_endpoint)

        self.assertEqual(400, response.status_code, msg="Missing id_asset")

        json_data['asset']['id_asset'] = 0
        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=json_data, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code, msg="Missing asset type")

        json_data['asset']['asset_type'] = 'application/octet-stream'

        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=json_data, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code, msg="Missing id_session")

        json_data['asset']['id_session'] = 2
        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=json_data, endpoint=self.test_endpoint)
        self.assertEqual(200, response.status_code, msg="Post new")  # All ok now!

        json_data = response.json[0]
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

        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=json_data, endpoint=self.test_endpoint)
        self.assertEqual(200, response.status_code, msg="Post update")
        json_data = response.json[0]
        self._checkJson(json_data, minimal=True)
        self.assertEqual(json_data['asset_name'], 'Test Asset 2')
        self.assertEqual(json_data['asset_service_uuid'], self.service_uuid)

        # Delete
        response = self._delete_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                        params={'uuid': current_uuid}, endpoint=self.test_endpoint)

        self.assertEqual(200, response.status_code, msg="Delete OK")

        # Bad delete
        response = self._delete_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                        params={'uuid': current_uuid}, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code, msg="Wrong delete")

    def test_get_endpoint_query_session_assets_as_admin_token_only(self):
        params = {'id_session': 2, 'with_urls': True, 'with_only_token': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)
        for data_item in response.json:
            self.assertFalse(data_item.__contains__("asset_name"))
            self.assertTrue(data_item.__contains__("asset_uuid"))
            self.assertTrue(data_item.__contains__("access_token"))
