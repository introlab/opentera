from typing import List
from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraService import TeraService


class ServiceQuerySessionTypesTest(BaseServiceAPITest):
    test_endpoint = '/api/service/sessiontypes'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import service_api_ns
        from BaseServiceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.service.ServiceQuerySessionTypes import ServiceQuerySessionTypes
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseServiceAPITest.getConfig())}
        service_api_ns.add_resource(ServiceQuerySessionTypes, '/sessiontypes', resource_class_kwargs=kwargs)

        # Setup token
        self.setup_service_token()

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        response = self.test_client.get(self.test_endpoint)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_and_invalid_params(self):
        params = {'unused1': True, 'unused2': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=None, endpoint=self.test_endpoint)
        self.assertEqual(200, response.status_code)

        session_types : list[TeraSessionType] = TeraSessionType.query.all()
        service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
        from modules.DatabaseModule.DBManager import DBManager
        service_access = DBManager.serviceAccess(service)
        accessible_types = service_access.get_accessible_sessions_types()
        self.assertEqual(len(accessible_types), len(response.json))
        self.assertTrue(len(accessible_types) <= len(session_types))
        for session_type in accessible_types:
            json_value = session_type.to_json()
            self.assertTrue(json_value in response.json)
