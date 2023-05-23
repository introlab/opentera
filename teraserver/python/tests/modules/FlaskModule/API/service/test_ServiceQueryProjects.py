from BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraServiceProject import TeraServiceProject


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

    def test_post_and_delete_endpoint_with_token(self):
        with self._flask_app.app_context():
            # Post with missing informations
            json_data = {
                'project_name': 'Testing123',
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing project struct")

            json_data = {
                'project': {
                    'project_name': 'Testing123'
                }
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_project")

            json_data['project']['id_project'] = 0
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_site")

            # Post in a site where service isn't associated
            json_data['project']['id_site'] = 2
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to site")

            # All good now
            json_data['project']['id_site'] = 1
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="New OK")
            project_data = response.json
            project_id = project_data['id_project']

            # Check that service was correctly associated to that new project
            sp: TeraServiceProject = TeraServiceProject.get_service_project_for_service_project(project_id=project_id,
                                                                                                service_id=
                                                                                                self.id_service)
            self.assertIsNotNone(sp)

            # Post update to project without association to service
            json_data = {
                'project': {
                    'id_project': 3,
                    'id_site': 2,
                    'project_name': 'New Project Name'
                }
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to project")

            json_data = {
                'project': {
                    'id_project': project_id,
                    'id_site': 2,
                    'project_name': 'New Project Name',
                    'invalid_parameter': -1
                }
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to site")

            del json_data['project']['id_site']
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(500, response.status_code, msg="Invalid parameter")

            del json_data['project']['invalid_parameter']
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Update OK")

            # Delete denied (not associated to service)
            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': 3})
            self.assertEqual(403, response.status_code, msg="Delete denied")

            # Delete with integrity error
            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': 1})
            self.assertEqual(500, response.status_code, msg="Delete denied (integrity)")

            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': project_id})
            self.assertEqual(200, response.status_code, msg="Delete OK")
