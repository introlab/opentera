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

    def test_endpoint_with_token_auth_with_device_uuid(self):
        # Get all devices from DB
        devices: list[TeraDevice] = TeraDevice.query.all()
        for device in devices:
            device_uuid: str = device.device_uuid
            params = {'device_uuid': device_uuid}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            device_json = device.to_json()
            self.assertEqual(device_json, response.json)
