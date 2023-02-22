from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject


class UserQueryTestTypeProjectTest(BaseUserAPITest):
    test_endpoint = '/api/user/testtypes/projects'

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

    def test_post_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_query_as_admin_with_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(400, response.status_code)

    def test_query_as_user_with_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user')
            self.assertEqual(400, response.status_code)

    def test_query_project_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 10}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json), 0)

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_project_with_test_type_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 2, 'with_test_types': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_test_type_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 30}  # Invalid
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_test_type': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_test_type_with_projects_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 1, 'with_projects': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_test_type_with_projects_and_with_sites_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 3, 'with_projects': 1, 'with_sites': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_site'))
                self.assertTrue(data_item.__contains__('site_name'))

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'list': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 2)

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_project_as_user(self):
        with self._flask_app.app_context():
            params = {'id_project': 10}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', 
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4', 
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', 
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_project_with_test_type_as_user(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'with_test_type': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_test_type_as_user(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 30}  # Invalid
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_test_type': 4}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_test_type': 2}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_test_type_with_projects_as_user(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 1, 'with_projects': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 2, 'list': 1}

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_post_test_type(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing everything")  # Missing

            json_data = {'test_type': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_test_type")

            json_data = {'test_type': {'id_test_type': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing projects")

            json_data = {'test_type': {'id_test_type': 1, 'projects': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only project/site admins can change things here")

            json_data = {'test_type': {'id_test_type': 3, 'projects': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove from all projects OK")

            params = {'id_test_type': 3}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            json_data = {'test_type': {'id_test_type': 3, 'projects': [{'id_project': 1},
                                                                       {'id_project': 2},
                                                                       {'id_project': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="One project not part of session type site")

            json_data = {'test_type': {'id_test_type': 3, 'projects': [{'id_project': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all projects OK")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))  # Everything was added

            json_data = {'test_type': {'id_test_type': 1, 'projects': [{'id_project': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove one project")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            json_data = {'test_type': {'id_test_type': 1, 'projects': [{'id_project': 1},
                                                                       {'id_project': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Back to initial")

    def test_post_project(self):
        with self._flask_app.app_context():
            # Project update
            json_data = {'project': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_project")

            json_data = {'project': {'id_project': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing test types")

            json_data = {'project': {'id_project': 1, 'testtypes': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only project admins can change things here")

            json_data = {'project': {'id_project': 1, 'testtypes': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove all test types OK")

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            json_data = {'project': {'id_project': 1, 'testtypes': [{'id_test_type': 1},
                                                                    {'id_test_type': 2},
                                                                    {'id_test_type': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="One test type not allowed - not part of the site project!")

            json_data = {'project': {'id_project': 1, 'testtypes': [{'id_test_type': 1},
                                                                    {'id_test_type': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="New test type association OK")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))  # Everything was added

            json_data = {'project': {'id_project': 1, 'testtypes': [{'id_test_type': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove 1 type")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            json_data = {'project': {'id_project': 1, 'testtypes': [{'id_test_type': 1},
                                                                    {'id_test_type': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Back to initial state")

    def test_post_test_type_project_and_delete(self):
        with self._flask_app.app_context():
            # TestType-Project update
            json_data = {'test_type_project': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'test_type_project': {'id_project': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'test_type_project': {'id_project': 1, 'id_test_type': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only project admins can change things here")

            json_data = {'test_type_project': {'id_project': 1, 'id_test_type': 3}}
            response = self._post_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Add new association not OK - type not part of the site")

            json_data = {'test_type_project': {'id_project': 2, 'id_test_type': 2}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add new association OK")

            params = {'id_project': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)

            current_id = None
            for dp in response.json:
                if dp['id_test_type'] == 2:
                    current_id = dp['id_test_type_project']
                    break
            self.assertFalse(current_id is None)

            response = self._delete_with_user_http_auth(self.test_client, username='user', password='user',
                                                        params={'id': current_id})
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params={'id': current_id})
            self.assertEqual(200, response.status_code, msg="Delete OK")

            params = {'id_project': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(TeraTestTypeProject.query.filter_by(id_project=2).count(), len(response.json))

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_test_type_project'))
        self.assertTrue(json_data.__contains__('id_test_type'))
        self.assertTrue(json_data.__contains__('id_project'))

        if not minimal:
            self.assertTrue(json_data.__contains__('test_type_name'))
            self.assertTrue(json_data.__contains__('project_name'))
        else:
            self.assertFalse(json_data.__contains__('test_type_name'))
            self.assertFalse(json_data.__contains__('project_name'))
