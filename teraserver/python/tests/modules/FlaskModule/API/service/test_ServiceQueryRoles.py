from BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraServiceRole import TeraServiceRole


class ServiceQueryRoles(BaseServiceAPITest):
    test_endpoint = '/api/service/roles'

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
                                                         params=None)
            self.assertEqual(200, response.status_code)
            roles = response.json
            wanted_roles = TeraServiceRole.get_service_roles(self.id_service)
            self.assertEqual(len(wanted_roles), len(roles))

            for role in roles:
                self._checkJson(role)
                self.assertEqual(self.id_service, role['id_service'])

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {
                'service_role': {
                }
            }

            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service_role")

            json_data['service_role']['id_service_role'] = 0
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing role name")

            json_data['service_role']['service_role_name'] = 'testrole'
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

            json_data = response.json
            current_id = json_data['id_service_role']
            role = TeraServiceRole.get_service_role_by_id(current_id)
            self.assertIsNotNone(role)

            json_data = {
                'service_role': {
                    'id_service_role': current_id,
                    'service_role_name': 'testrole2'
                }
            }
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data)
            self.assertEqual(response.status_code, 200, msg="Update OK")

            json_data = response.json
            role = TeraServiceRole.get_service_role_by_id(current_id)
            self.assertEqual(role.service_role_name, json_data['service_role_name'])
            self.assertEqual(json_data['service_role_name'], 'testrole2')
            self.assertEqual(json_data['id_service'], self.id_service)

            params = {'id': current_id}
            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': 1})
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params=params)
            self.assertEqual(response.status_code, 200, msg="Delete OK")

            role = TeraServiceRole.get_service_role_by_id(current_id)
            self.assertIsNone(role)

    def _checkJson(self, json_data, minimal=False):
        self.assertTrue(json_data.__contains__('id_service_role'))
        self.assertTrue(json_data.__contains__('id_service'))
        if not minimal:
            if json_data.__contains__('id_site'):
                self.assertTrue(json_data.__contains__('site_name'))
            if json_data.__contains__('id_project'):
                self.assertTrue(json_data.__contains__('project_name'))
            self.assertTrue(json_data.__contains__('service_name'))
        else:
            if json_data.__contains__('id_site'):
                self.assertFalse(json_data.__contains__('site_name'))
            if json_data.__contains__('id_project'):
                self.assertFalse(json_data.__contains__('project_name'))
            self.assertFalse(json_data.__contains__('service_name'))
