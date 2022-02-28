from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app


class ServiceQueryParticipantsTest(BaseServiceAPITest):
    test_endpoint = '/api/service/services'

    def setUp(self):
        from modules.FlaskModule.FlaskModule import service_api_ns
        from BaseServiceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.service.ServiceQueryServices import ServiceQueryServices
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseServiceAPITest.getConfig())}
        service_api_ns.add_resource(ServiceQueryServices, '/services', resource_class_kwargs=kwargs)

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
