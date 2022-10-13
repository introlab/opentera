from typing import List

from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceSubType import TeraDeviceSubType
from opentera.db.models.TeraDeviceType import TeraDeviceType


class ServiceQueryAccessTest(BaseServiceAPITest):
    test_endpoint = '/api/service/access'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import service_api_ns
        from BaseServiceAPITest import FakeFlaskModule

        # Setup minimal API
        from modules.FlaskModule.API.service.ServiceQueryAccess import ServiceQueryAccess
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseServiceAPITest.getConfig())}
        service_api_ns.add_resource(ServiceQueryAccess, '/access', resource_class_kwargs=kwargs)

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



