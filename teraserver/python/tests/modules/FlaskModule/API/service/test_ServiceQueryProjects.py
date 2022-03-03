from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraProject import TeraProject


class ServiceQueryProjectsTest(BaseServiceAPITest):
    test_endpoint = '/api/service/projects'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import service_api_ns
        from BaseServiceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.service.ServiceQueryProjects import ServiceQueryProjects
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseServiceAPITest.getConfig())}
        service_api_ns.add_resource(ServiceQueryProjects, '/projects', resource_class_kwargs=kwargs)

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

    def test_get_endpoint_with_token_auth_and_invalid_id_project(self):
        params = {'id_project': -1}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token, params=params,
                                                     endpoint=self.test_endpoint)
        self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_token_auth_and_valid_id_project(self):
        params = {'id_project': 1}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token, params=params,
                                                     endpoint=self.test_endpoint)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json))
        project: TeraProject = TeraProject.get_project_by_id(1)
        self.assertEqual(project.to_json(minimal=True), response.json[0])

    def test_get_endpoint_with_token_auth_and_valid_but_denied_id_project(self):
        denied_id_projects = [2, 3]

        for id_project in denied_id_projects:
            params = {'id_project': id_project}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)
