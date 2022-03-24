from typing import List

from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceSubType import TeraDeviceSubType
from opentera.db.models.TeraDeviceType import TeraDeviceType


class ServiceQueryDevicesTest(BaseServiceAPITest):
    test_endpoint = '/api/service/devices'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import service_api_ns
        from BaseServiceAPITest import FakeFlaskModule

        # Setup minimal API
        from modules.FlaskModule.API.service.ServiceQueryDevices import ServiceQueryDevices
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseServiceAPITest.getConfig())}
        service_api_ns.add_resource(ServiceQueryDevices, '/devices', resource_class_kwargs=kwargs)

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

    def test_get_endpoint_with_token_auth_with_wrong_params(self):
        # Get all devices from DB
        devices: List[TeraDevice] = TeraDevice.query.all()
        for device in devices:
            device_uuid: str = device.device_uuid
            params = {'device_uuid_wrong': device_uuid}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_with_device_uuid(self):
        # Get all devices from DB
        devices: List[TeraDevice] = TeraDevice.query.all()
        for device in devices:
            device_uuid: str = device.device_uuid
            params = {'device_uuid': device_uuid}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertFalse('device_type' in response.json)
            self.assertFalse('device_subtype' in response.json)
            self.assertFalse('device_assets' in response.json)
            device_json = device.to_json()
            self.assertEqual(device_json, response.json)

    def test_get_endpoint_with_token_auth_with_device_uuid_and_device_type(self):
        # Get all devices from DB
        devices: List[TeraDevice] = TeraDevice.query.all()
        for device in devices:
            device_uuid: str = device.device_uuid
            params = {'device_uuid': device_uuid, 'with_device_type': True}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertTrue('device_type' in response.json)
            self.assertFalse('device_subtype' in response.json)
            self.assertFalse('device_assets' in response.json)
            device_json = device.to_json()
            device_json['device_type'] = TeraDeviceType.get_device_type_by_id(device.id_device_type).\
                to_json(minimal=True)
            self.assertEqual(device_json, response.json)

    def test_get_endpoint_with_token_auth_with_device_uuid_and_device_subtype(self):
        # Get all devices from DB
        devices: List[TeraDevice] = TeraDevice.query.all()
        for device in devices:
            device_uuid: str = device.device_uuid
            params = {'device_uuid': device_uuid, 'with_device_subtype': True}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertFalse('device_type' in response.json)
            self.assertTrue('device_subtype' in response.json)
            self.assertFalse('device_assets' in response.json)

            device_json = device.to_json()

            if device.id_device_subtype is not None:
                device_subtype = TeraDeviceSubType.get_device_subtype_by_id(device.id_device_subtype)
                device_json['device_subtype'] = device_subtype.to_json(minimal=True)
            else:
                device_json['device_subtype'] = None
            self.assertEqual(device_json, response.json)

    def test_get_endpoint_with_token_auth_with_device_uuid_and_device_assets(self):
        # Get all devices from DB
        devices: List[TeraDevice] = TeraDevice.query.all()
        for device in devices:
            device_uuid: str = device.device_uuid
            params = {'device_uuid': device_uuid, 'with_device_assets': True}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertFalse('device_type' in response.json)
            self.assertFalse('device_subtype' in response.json)
            self.assertTrue('device_assets' in response.json)
            device_json = device.to_json()
            device_json['device_assets'] = []
            from modules.DatabaseModule.DBManager import db
            # Required for lazy loading, why ?
            db.session.add(device)

            for asset in device.device_assets:
                device_json['device_assets'].append(asset.to_json(minimal=True))

            self.assertEqual(device_json, response.json)
            db.session.rollback()

    def test_post_endpoint_without_token_auth(self):
        response = self.test_client.post(self.test_endpoint, json={})
        self.assertEqual(401, response.status_code)

    def test_post_endpoint_with_token_auth_empty_json(self):

        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code)

    def test_post_endpoint_with_token_auth_create_device(self):
        device_schema = {
            'device': {
                'id_device': 0,
                'id_device_type': 1,
                'id_device_subtype': 0,
                'device_name': 'test_device',
                'device_enabled': True,
                'device_onlineable': True
            }
        }

        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=device_schema, endpoint=self.test_endpoint)

        self.assertEqual(200, response.status_code)
        id_device = response.json['id_device']

        device: TeraDevice = TeraDevice.get_device_by_id(id_device)
        self.assertEqual(response.json, device.to_json(minimal=False))

    def test_post_endpoint_with_token_auth_update_device(self):
        # Only required fields
        device_schema = {
            'device': {
                'id_device': 1,
                'id_device_type': 1,
                'id_device_subtype': 0,
                'device_name': 'test_device',
                'device_enabled': True,
                'device_onlineable': True
            }
        }

        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=device_schema, endpoint=self.test_endpoint)

        self.assertEqual(200, response.status_code)
        device: TeraDevice = TeraDevice.get_device_by_id(1)
        self.assertEqual('test_device', device.device_name)
        self.assertEqual(1, device.id_device_type)
        self.assertEqual(None, device.id_device_subtype)