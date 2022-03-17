from typing import List

from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraService import TeraService


class ServiceQueryServicesTest(BaseServiceAPITest):
    test_endpoint = '/api/service/services'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import service_api_ns
        from BaseServiceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.service.ServiceQueryServices import ServiceQueryServices
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseServiceAPITest.getConfig())}
        service_api_ns.add_resource(ServiceQueryServices, '/services', resource_class_kwargs=kwargs)

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

    def test_get_endpoint_with_token_auth_and_invalid_params(self):
        params = {'my_invalid_param': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_and_id_service(self):

        services: List[TeraService] = TeraService.query.all()
        for service in services:
            params = {'id_service': service.id_service}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self.assertEqual(service.id_service, response.json[0]['id_service'])
            self.assertEqual(service.to_json(minimal=True), response.json[0])

    def test_get_endpoint_with_token_auth_and_id_service_with_base_url(self):

        services: List[TeraService] = TeraService.query.all()
        for service in services:
            params = {
                'id_service': service.id_service,
                'with_base_url': True
            }
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self.assertEqual(service.id_service, response.json[0]['id_service'])
            self.assertTrue('service_base_url' in response.json[0])

    def test_get_endpoint_with_token_auth_and_uuid_service(self):

        services: List[TeraService] = TeraService.query.all()
        for service in services:
            params = {'uuid_service': service.service_uuid}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self.assertEqual(service.service_uuid, response.json[0]['service_uuid'])
            self.assertEqual(service.to_json(minimal=True), response.json[0])

    def test_get_endpoint_with_token_auth_and_uuid_service_with_base_url(self):

        services: List[TeraService] = TeraService.query.all()
        for service in services:
            params = {
                'uuid_service': service.service_uuid,
                'with_base_url': True
            }
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self.assertEqual(service.service_uuid, response.json[0]['service_uuid'])
            self.assertTrue('service_base_url' in response.json[0])

    def test_get_endpoint_with_token_auth_and_service_key(self):

        services: List[TeraService] = TeraService.query.all()
        for service in services:
            params = {'service_key': service.service_key}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self.assertEqual(service.service_key, response.json[0]['service_key'])
            self.assertEqual(service.to_json(minimal=True), response.json[0])

    def test_get_endpoint_with_token_auth_and_service_key_with_base_url(self):

        services: List[TeraService] = TeraService.query.all()
        for service in services:
            params = {
                'service_key': service.service_key,
                'with_base_url': True
            }
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self.assertEqual(service.service_key, response.json[0]['service_key'])
            self.assertTrue('service_base_url' in response.json[0])
