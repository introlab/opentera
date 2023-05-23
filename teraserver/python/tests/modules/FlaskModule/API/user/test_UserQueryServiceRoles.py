from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraServiceRole import TeraServiceRole


class UserQueryServiceRolesTest(BaseUserAPITest):
    test_endpoint = '/api/user/services/roles'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.delete(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_service_roles_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(200, response.status_code)
            roles_count = TeraServiceRole.get_count()
            self.assertEqual(roles_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(roles_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'globals': 1})
            self.assertEqual(200, response.status_code)
            roles_count = TeraServiceRole.get_count(filters={'id_project': None, 'id_site': None})
            self.assertEqual(roles_count, len(response.json))
            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_get_service_roles_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3')
            self.assertEqual(200, response.status_code)
            roles_count = TeraServiceRole.get_count()
            self.assertGreater(roles_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'list': 1})
            self.assertEqual(200, response.status_code)

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'globals': 1})
            self.assertEqual(200, response.status_code)
            roles_count = TeraServiceRole.get_count(filters={'id_project': None, 'id_site': None})
            self.assertGreater(roles_count, len(response.json))
            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_get_specific_service_roles_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 2})
            self.assertEqual(200, response.status_code)
            roles_count = TeraServiceRole.get_count(filters={'id_service': 2})
            self.assertEqual(roles_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'list': 1, 'id_service': 2})
            self.assertEqual(200, response.status_code)
            self.assertEqual(roles_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'globals': 1, 'id_service': 2})
            self.assertEqual(200, response.status_code)
            roles_count = TeraServiceRole.get_count(filters={'id_project': None, 'id_site': None, 'id_service': 2})
            self.assertEqual(roles_count, len(response.json))
            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_get_specific_service_roles_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'id_service': 2})
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json), msg='No access to service')

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'id_service': 3})
            roles_count = TeraServiceRole.get_count(filters={'id_service': 3})
            self.assertEqual(roles_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'list': 1, 'id_service': 3})
            self.assertEqual(200, response.status_code)
            self.assertEqual(roles_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'globals': 1, 'id_service': 3})
            self.assertEqual(200, response.status_code)
            roles_count = TeraServiceRole.get_count(filters={'id_project': None, 'id_site': None, 'id_service': 3})
            self.assertEqual(roles_count, len(response.json))
            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {
                'service_role': {
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service_role")

            json_data['service_role']['id_service_role'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service")

            json_data['service_role']['id_service'] = 2
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing role name")

            json_data['service_role']['service_role_name'] = 'testrole'
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
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
            response = self._post_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                      json=json_data)
            self.assertEqual(response.status_code, 403, msg="Update denied")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Update OK")
            json_data = response.json
            role = TeraServiceRole.get_service_role_by_id(current_id)
            self.assertEqual(role.service_role_name, json_data['service_role_name'])
            self.assertEqual(json_data['service_role_name'], 'testrole2')
            self.assertEqual(json_data['id_service'], 2)

            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
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
