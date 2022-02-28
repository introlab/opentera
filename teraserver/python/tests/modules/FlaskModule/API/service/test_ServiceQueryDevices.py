from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from modules.FlaskModule.API.service.ServiceQueryDevices import ServiceQueryDevices
from opentera.db.models.TeraDevice import TeraDevice


class ServiceQueryDevicesTest(BaseServiceAPITest):
    test_endpoint = '/api/service/devices'

    def setUp(self):
        from modules.FlaskModule.FlaskModule import service_api_ns
        from BaseServiceAPITest import FakeFlaskModule
        # Setup minimal API
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseServiceAPITest.getConfig())}
        service_api_ns.add_resource(ServiceQueryDevices, '/devices', resource_class_kwargs=kwargs)

        # Setup token
        self.setup_service_token()

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        pass

    def test_endpoint_no_auth(self):
        response = self.test_client.get(self.test_endpoint)
        self.assertEqual(401, response.status_code)

    def test_endpoint_with_token_auth_no_params(self):
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=None, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code)

    def test_endpoint_with_token_auth_with_wrong_params(self):
        # Get all devices from DB
        devices: list[TeraDevice] = TeraDevice.query.all()
        for device in devices:
            device_uuid: str = device.device_uuid
            params = {'device_uuid_wrong': device_uuid}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_endpoint_with_token_auth_with_device_uuid(self):
        # Get all devices from DB
        devices: list[TeraDevice] = TeraDevice.query.all()
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

    def test_endpoint_with_token_auth_with_device_uuid_and_device_type(self):
        # Get all devices from DB
        devices: list[TeraDevice] = TeraDevice.query.all()
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
            device_json['device_type'] = device.device_type.to_json(minimal=True)
            self.assertEqual(device_json, response.json)

    def test_endpoint_with_token_auth_with_device_uuid_and_device_subtype(self):
        # Get all devices from DB
        devices: list[TeraDevice] = TeraDevice.query.all()
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
            from modules.DatabaseModule.DBManager import db
            # Required for lazy loading
            db.session.add(device)
            if device.device_subtype is not None:
                device_json['device_subtype'] = device.device_subtype.to_json(minimal=True)
            else:
                device_json['device_subtype'] = None
            self.assertEqual(device_json, response.json)
            db.session.rollback()

    def test_endpoint_with_token_auth_with_device_uuid_and_device_subtype(self):
        # Get all devices from DB
        devices: list[TeraDevice] = TeraDevice.query.all()
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
            from modules.DatabaseModule.DBManager import db
            # Required for lazy loading, why ?
            db.session.add(device)
            if device.device_subtype is not None:
                device_json['device_subtype'] = device.device_subtype.to_json(minimal=True)
            else:
                device_json['device_subtype'] = None
            self.assertEqual(device_json, response.json)
            db.session.rollback()

    def test_endpoint_with_token_auth_with_device_uuid_and_device_assets(self):
        # Get all devices from DB
        devices: list[TeraDevice] = TeraDevice.query.all()
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