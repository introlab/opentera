from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest

import datetime


class UserQueryAssetsTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/assets'

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

    def test_query_bad_params_as_admin(self):
        params = {'id_invalid': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 400)

    def test_query_tera_server_assets_as_admin(self):
        payload = {'service_uuid': '00000000-0000-0000-0000-000000000001'}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload)
        self.assertEqual(response.status_code, 200)

    def test_query_tera_server_assets_no_access(self):
        payload = {'service_uuid': '00000000-0000-0000-0000-000000000001'}
        response = self._request_with_http_auth(username='user4', password='user4', payload=payload)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)
        self.assertEqual(response.status_code, 200)

    def test_query_device_assets_as_admin(self):
        payload = {'id_device': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_device_assets_no_access(self):
        payload = {'id_device': 1}
        response = self._request_with_http_auth(username='user4', password='user4', payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_session_assets_as_admin(self):
        payload = {'id_session': 2}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 3)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_session_assets_no_access(self):
        payload = {'id_session': 2}
        response = self._request_with_http_auth(username='user4', password='user4', payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_participant_assets_as_admin(self):
        payload = {'id_participant': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 4)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_participant_assets_no_access(self):
        payload = {'id_participant': 1}
        response = self._request_with_http_auth(username='user4', password='user4', payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_user_assets_as_admin(self):
        payload = {'id_user': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 4)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_user_assets_no_access(self):
        payload = {'id_user': 1}
        response = self._request_with_http_auth(username='user4', password='user4', payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_asset_as_admin(self):
        payload = {'id_asset': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_asset_no_access(self):
        payload = {'id_asset': 1}
        response = self._request_with_http_auth(username='user4', password='user4', payload=payload)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)
        self.assertEqual(response.status_code, 200)

    def test_query_assets_created_by_service_as_admin(self):
        payload = {'id_creator_service': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_assets_created_by_service_no_access(self):
        payload = {'id_creator_service': 1}
        response = self._request_with_http_auth(username='user4', password='user4', payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_assets_created_by_user_as_admin(self):
        payload = {'id_creator_user': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_assets_created_by_user_no_access(self):
        payload = {'id_creator_user': 1}
        response = self._request_with_http_auth(username='user4', password='user4', payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_assets_created_by_participant_as_admin(self):
        payload = {'id_creator_participant': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_assets_created_by_participant_no_access(self):
        payload = {'id_creator_participant': 1}
        response = self._request_with_http_auth(username='user4', password='user4', payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_query_assets_created_by_device_as_admin(self):
        payload = {'id_creator_device': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=payload)
        self.assertEqual(response.status_code, 200)

        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_assets_created_by_device_no_access(self):
        payload = {'id_creator_device': 1}
        response = self._request_with_http_auth(username='user4', password='user4', payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_post_as_admin(self):
        # Creating fake data
        import io
        f = io.BytesIO(b"\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x01\x01\x01\x01")
        files = {'upload_file': ('foobar.txt', f, 'text/x-spam')}
        params = {'id_session': 1}
        response = self._post_file_with_http_auth(username='admin', password='admin',
                                                  params=params, files=files)
        # self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 501)

    def test_delete_as_admin(self):
        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=1)
        self.assertEqual(response.status_code, 501)

    # def test_post_as_admin_huge(self):
    #     # Creating fake data
    #     import io
    #     import os
    #     # 1 MB file
    #     f = io.BytesIO(os.urandom(1024 * 1024 * 1))
    #     files = {'upload_file': ('foobar.txt', f, 'text/x-spam')}
    #     params = {'id_session': 1}
    #     response = self._post_file_with_http_auth(username='admin', password='admin',
    #                                               params=params, files=files)
    #     self.assertEqual(response.status_code, 200)

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
        self.assertTrue(json_data.__contains__('asset_infos_url'))
        self.assertTrue(json_data.__contains__('asset_url'))
