from BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSite import TeraSite


class ServiceQueryProjectsTest(BaseServiceAPITest):
    test_endpoint = '/api/service/projects'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_and_invalid_id_project(self):
        with self._flask_app.app_context():
            params = {'id_project': -1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_token_auth_and_valid_id_project(self):
        with self._flask_app.app_context():
            params = {'id_project': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            project: TeraProject = TeraProject.get_project_by_id(1)
            self.assertEqual(project.to_json(minimal=True), response.json[0])

    def test_get_endpoint_with_token_auth_and_valid_but_denied_id_project(self):
        with self._flask_app.app_context():
            denied_id_projects = [2, 3]

            for id_project in denied_id_projects:
                params = {'id_project': id_project}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_token_auth_and_invalid_id_site(self):
        with self._flask_app.app_context():
            params = {'id_site': -1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_token_auth_and_denied_id_site(self):
        with self._flask_app.app_context():
            params = {'id_site': 2}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_token_auth_and_id_site(self):
        with self._flask_app.app_context():
            params = {'id_site': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            site: TeraSite = TeraSite.get_site_by_id(1)
            self.assertEqual(len(site.site_projects), len(response.json))
            for json_project in response.json:
                project: TeraProject = TeraProject.get_project_by_id(json_project['id_project'])
                self.assertEqual(project.to_json(minimal=True), json_project)
