from BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models import TeraParticipantGroup


class ServiceQueryParticipantGroupsTest(BaseServiceAPITest):
    test_endpoint = '/api/service/groups'

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


    def test_get_endpoint_with_token_auth_and_invalid_id_participant_group(self):
        with self._flask_app.app_context():
            params = {'id_participant_group': -1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)


    def test_get_endpoint_with_token_auth_and_invalid_id_project_and_invalid_id_participant_group(self):
        with self._flask_app.app_context():
            params = {'id_project': -1, 'id_participant_group': -1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)


    def test_get_endpoint_with_token_auth_and_valid_id_participant_group(self):
        with self._flask_app.app_context():
            params = {'id_participant_group': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(3, len(response.json))
            group: TeraParticipantGroup = TeraParticipantGroup.get_participant_group_by_id(1)
            self.assertEqual(group.to_json(minimal=True), response.json)


    def test_get_endpoint_with_token_auth_and_valid_id_project(self):
        with self._flask_app.app_context():
            params = {'id_project': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertGreaterEqual(len(response.json),1 )
            groups: TeraParticipantGroup = TeraParticipantGroup.get_participant_group_for_project(1)
            i = 0
            for group in groups:
                self.assertEqual(group.to_json(minimal=True), response.json[i])
                i = i + 1

    def test_get_endpoint_with_token_auth_and_valid_id_project_and_valid_id_participant_group(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'id_participant_group': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)

    def test_get_endpoint_with_token_auth_and_valid_but_denied_id_project(self):
        with self._flask_app.app_context():
            denied_id_projects = [2, 3]

            for id_project in denied_id_projects:
                params = {'id_project': id_project}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(403, response.status_code)


    def test_get_endpoint_with_token_auth_and_valid_but_denied_id_participant_group(self):
        with self._flask_app.app_context():
            params = {'id_participant_group': 2}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)



    def test_post_and_delete_endpoint_with_token(self):
        with self._flask_app.app_context():
            # Test case: Post with missing information
            json_data = {
                'participant_group_name': 'Testing123',
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing project struct")

            # Test case: Post with missing id_project
            json_data = {
                'participant_group': {
                    'participant_group_name': 'Testing123'
                }
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_project")

            # Test case: Post with missing id_participant_group
            json_data = {
                'participant_group': {
                    'participant_group_name': 'Testing123',
                    'id_project': 1
                }
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_participant_group")

            json_data['participant_group']['id_project'] = 2
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_participant_group")

            # Test case: Post in a project where service isn't associated
            json_data['participant_group']['id_project'] = 2
            json_data['participant_group']['id_participant_group'] = 0
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to project")

            # Test case: Modification
            json_data['participant_group']['id_participant_group'] = 1
            json_data['participant_group']['id_project'] = 1
            json_data['participant_group']['participant_group_name'] = "New name"
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(200, response.status_code, msg="New OK")
            group_data = response.json
            project_id = group_data['id_project']
            name = group_data['participant_group_name']
            self.assertEqual(1, project_id)
            self.assertEqual("New name", name)


            # Test case: Creation
            json_data['participant_group']['id_participant_group'] = 0
            json_data['participant_group']['id_project'] = 1
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(200, response.status_code, msg="New OK")
            group_data = response.json
            project_id = group_data['id_project']
            self.assertEqual(1, project_id)


            # Test case: Post update to project without association to service
            json_data = {
                'participant_group': {
                    'id_project': 3,
                    'id_participant_group': 0,
                    'participant_group_name': 'Testing123'
                }
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to project")

            # Test case: Post update to group without association to service
            json_data = {
                'participant_group': {
                    'id_project': 1,
                    'id_participant_group': 2,
                    'participant_group_name': 'Testing123',
                    'invalid_parameter': -1
                }
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to the group")

            # Test case: Post update with invalid parameter
            del json_data['participant_group']['id_project']
            json_data['participant_group']['id_participant_group'] = 3
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(500, response.status_code, msg="Invalid parameter")


            del json_data['participant_group']['invalid_parameter']
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(200, response.status_code, msg="Update OK")

            # Test case: Modification
            json_data['participant_group']['id_participant_group'] = 1
            json_data['participant_group']['id_project'] = 1
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(200, response.status_code, msg="New OK")

            # Test case: Delete denied (not associated to service)
            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': 2})
            self.assertEqual(403, response.status_code, msg="Delete denied")

            # Test case: Delete with integrity error
            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': 1})
            self.assertEqual(500, response.status_code, msg="Delete denied (integrity)")

            # Test case: Delete with no problem
            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': 3})
            self.assertEqual(200, response.status_code, msg="Delete OK")