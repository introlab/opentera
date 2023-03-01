from BaseUserAPITest import BaseUserAPITest


class UserQueryAssetsTest(BaseUserAPITest):
    test_endpoint = '/api/user/assets'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            with self._flask_app.app_context():
                response = self.test_client.get(self.test_endpoint)
                self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            with self._flask_app.app_context():
                response = self._get_with_user_http_auth(self.test_client)
                self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            with self._flask_app.app_context():
                response = self._get_with_user_token_auth(self.test_client)
                self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            params = {'id': 0}
            response = self.test_client.delete(self.test_endpoint, query_string=params)
            self.assertEqual(401, response.status_code)

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(400, response.status_code)

    def test_query_bad_params_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_invalid': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(400, response.status_code)

    def test_query_tera_server_assets_as_admin(self):
        with self._flask_app.app_context():
            params = {'service_uuid': '00000000-0000-0000-0000-000000000001'}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)

    def test_query_tera_server_assets_no_access(self):
        with self._flask_app.app_context():
            params = {'service_uuid': '00000000-0000-0000-0000-000000000001'}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 0)
        
    def test_query_device_assets_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_device': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_device_assets_no_access(self):
        with self._flask_app.app_context():
            params = {'id_device': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_session_assets_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_session': 2, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json), 3)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_assets_no_access(self):
        with self._flask_app.app_context():
            params = {'id_session': 2}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_participant_assets_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_participant': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json), 4)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_participant_assets_no_access(self):
        with self._flask_app.app_context():
            params = {'id_participant': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_user_assets_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_user': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 4)

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_user_assets_no_access(self):
        with self._flask_app.app_context():
            params = {'id_user': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_asset_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_asset': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_asset_no_access(self):
        with self._flask_app.app_context():
            params = {'id_asset': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 0)

    def test_query_assets_created_by_service_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_creator_service': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json), 0)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_assets_created_by_service_no_access(self):
        with self._flask_app.app_context():
            params = {'id_creator_service': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_assets_created_by_user_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_creator_user': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_assets_created_by_user_no_access(self):
        with self._flask_app.app_context():
            params = {'id_creator_user': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_assets_created_by_participant_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_creator_participant': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_assets_created_by_participant_no_access(self):
        with self._flask_app.app_context():
            params = {'id_creator_participant': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_assets_created_by_device_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_creator_device': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_assets_created_by_device_no_access(self):
        with self._flask_app.app_context():
            params = {'id_creator_device': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_post_as_admin(self):
        with self._flask_app.app_context():
            # Creating fake data
            import io
            f = io.BytesIO(b"\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x01\x01\x01\x01")
            files = {'upload_file': (f, 'data.raw')}
            params = {'id_session': 1}
            response = self._post_file_with_user_http_auth(self.test_client, files, username='admin', password='admin',
                                                           params=params)
            # Not implemented directly, should go through FileTransferService
            self.assertEqual(501, response.status_code)

    def test_delete_as_admin(self):
        with self._flask_app.app_context():
            params = {'id': 1}
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(501, response.status_code)

    def test_query_session_assets_as_admin_token_only(self):
        with self._flask_app.app_context():
            params = {'id_session': 2, 'with_urls': True, 'with_only_token': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 3)
            for data_item in response.json:
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
