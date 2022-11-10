from typing import List
from BaseDeviceAPITest import BaseDeviceAPITest
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraAsset import TeraAsset


class DeviceQueryAssetsTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/assets'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_device_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_param(self):
        with self._flask_app.app_context():
            devices: List[TeraDevice] = TeraDevice.query.all()
            for device in devices:
                if device.device_token:
                    if device.device_enabled:
                        response = self._get_with_device_token_auth(self.test_client, token=device.device_token)
                        self.assertEqual(200, response.status_code)

                        for asset_json in response.json:
                            self._checkJson(asset_json, minimal=True)

                    else:
                        response = self._get_with_device_token_auth(self.test_client, token=device.device_token)
                        self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_with_urls(self):
        with self._flask_app.app_context():
            devices: List[TeraDevice] = TeraDevice.query.all()
            params = {
                'with_urls': True
            }
            for device in devices:
                if device.device_token:
                    if device.device_enabled:
                        response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                    params=params)
                        self.assertEqual(200, response.status_code)

                        for asset_json in response.json:
                            self._checkJson(asset_json, minimal=False)

                    else:
                        response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                    params=params)
                        self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_with_asset_uuid(self):
        with self._flask_app.app_context():
            devices: List[TeraDevice] = TeraDevice.query.all()

            for device in devices:
                for asset in TeraAsset.get_assets_for_device(device.id_device):
                    self.assertEqual(asset.id_device, device.id_device)
                    params = {
                        'asset_uuid': asset.asset_uuid,
                        'with_urls': True
                    }

                    if device.device_token:
                        if device.device_enabled:
                            response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                        params=params)
                            self.assertEqual(200, response.status_code)

                            for asset_json in response.json:
                                self.assertEqual(asset.asset_uuid, asset_json['asset_uuid'])
                                self._checkJson(asset_json, minimal=False)

                        else:
                            response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                        params=params)
                            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_with_asset_id(self):
        with self._flask_app.app_context():
            devices: List[TeraDevice] = TeraDevice.query.all()

            for device in devices:
                for asset in TeraAsset.get_assets_for_device(device.id_device):
                    self.assertEqual(asset.id_device, device.id_device)
                    params = {
                        'id_asset': asset.id_asset,
                        'with_urls': True
                    }

                    if device.device_token:
                        if device.device_enabled:
                            response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                        params=params)
                            self.assertEqual(200, response.status_code)

                            for asset_json in response.json:
                                self.assertEqual(asset.id_asset, asset_json['id_asset'])
                                self._checkJson(asset_json, minimal=False)

                        else:
                            response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                        params=params)
                            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_with_forbidden_id_asset(self):
        with self._flask_app.app_context():
            devices: List[TeraDevice] = TeraDevice.query.all()

            for device in devices:
                for asset in TeraAsset.query.all():
                    params = {
                        'id_asset': asset.id_asset,
                        'with_urls': True
                    }

                    if device.device_token:
                        if device.device_enabled:
                            if asset.id_device != device.id_device:
                                response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                            params=params)
                                # TODO should have 403 instead?
                                self.assertEqual(200, response.status_code)
                                self.assertEqual(0, len(response.json))

                        else:
                            response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                        params=params)
                            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_with_forbidden_uuid_asset(self):
        with self._flask_app.app_context():
            devices: List[TeraDevice] = TeraDevice.query.all()

            for device in devices:
                for asset in TeraAsset.query.all():
                    params = {
                        'asset_uuid': asset.asset_uuid,
                        'with_urls': True
                    }

                    if device.device_token:
                        if device.device_enabled:
                            if asset.id_device != device.id_device:
                                response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                            params=params)
                                # TODO should have 403 instead?
                                self.assertEqual(200, response.status_code)
                                self.assertEqual(0, len(response.json))

                        else:
                            response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                        params=params)
                            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_with_token_only(self):
        with self._flask_app.app_context():
            devices: List[TeraDevice] = TeraDevice.query.all()

            for device in devices:
                for asset in TeraAsset.get_assets_for_device(device.id_device):
                    self.assertEqual(asset.id_device, device.id_device)
                    params = {
                        'id_asset': asset.id_asset,
                        'with_only_token': True
                    }

                    if device.device_token:
                        if device.device_enabled:
                            response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                        params=params)
                            self.assertEqual(200, response.status_code)
                            for json_asset in response.json:
                                self.assertFalse('asset_name' in json_asset)
                                self.assertTrue('asset_uuid' in json_asset)
                                self.assertTrue('access_token' in json_asset)
                        else:
                            response = self._get_with_device_token_auth(self.test_client, token=device.device_token,
                                                                        params=params)
                            self.assertEqual(401, response.status_code)

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
