from BaseUserAPITest import BaseUserAPITest


class UserQuerySessionTypeProjectTest(BaseUserAPITest):
    test_endpoint = '/api/user/sessiontypes/projects'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client)
            self.assertEqual(401, response.status_code)

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='admin', password='admin', client=self.test_client)
            self.assertEqual(response.status_code, 400)

    def test_query_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='user', password='user', params="",
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 400)

    def test_query_project_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 10}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 5)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_project_with_session_type_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 2, 'with_session_type': 1}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 5)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_session_type_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 30}  # Invalid
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_session_type': 2}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_session_type_with_projects_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 1, 'with_projects': 1}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 3)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_session_type_with_projects_and_with_sites_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 3, 'with_projects': 1, 'with_sites': 1}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 3)

            for data_item in json_data:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_site'))
                self.assertTrue(data_item.__contains__('site_name'))

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'list': 1}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 5)

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_project_as_user(self):
        with self._flask_app.app_context():
            params = {'id_project': 10}
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(username='user4', password='user4', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 5)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_project_with_session_type_as_user(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'with_session_type': 1}
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 5)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_session_type_as_user(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 30}  # Invalid
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_session_type': 4}
            response = self._get_with_user_http_auth(username='user4', password='user4', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_session_type': 2}
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_session_type_with_projects_as_user(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 1, 'with_projects': 1}
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 2, 'list': 1}

            response = self._get_with_user_http_auth(username='user4', password='user4', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)

    def test_post_session_type(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing everything")  # Missing

            json_data = {'session_type': {}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing id_session_type")

            json_data = {'session_type': {'id_session_type': 1}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing projects")

            json_data = {'session_type': {'id_session_type': 1, 'projects': []}}
            response = self._post_with_user_http_auth(username='user', password='user', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Only project/site admins can change things here")

            json_data = {'session_type': {'id_session_type': 2, 'projects': []}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Remove from all projects OK")

            params = {'id_session_type': 2}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)  # Everything was deleted!

            json_data = {'session_type': {'id_session_type': 2, 'projects': [{'id_project': 1},
                                                                             {'id_project': 2},
                                                                             {'id_project': 3}]}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="One project not part of session type site")

            json_data = {'session_type': {'id_session_type': 2, 'projects': [{'id_project': 1},
                                                                             {'id_project': 2}]}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Add all projects OK")

            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 2)  # Everything was added

            json_data = {'session_type': {'id_session_type': 2, 'projects': [{'id_project': 1}]}}
            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin',
                                                      json=json_data, client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Remove one project")

            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)

    def test_post_project(self):
        with self._flask_app.app_context():
            # Project update
            json_data = {'project': {}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing id_project")

            json_data = {'project': {'id_project': 1}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing session types")

            json_data = {'project': {'id_project': 1, 'sessiontypes': []}}
            response = self._post_with_user_http_auth(username='user', password='user', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

            json_data = {'project': {'id_project': 1, 'sessiontypes': []}}
            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Remove all session types OK")

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)  # Everything was deleted!

            json_data = {'project': {'id_project': 1, 'sessiontypes': [{'id_session_type': 1},
                                                                       {'id_session_type': 2},
                                                                       {'id_session_type': 6}]}}
            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403,
                             msg="One session type not allowed - not part of the site project!")

            json_data = {'project': {'id_project': 1, 'sessiontypes': [{'id_session_type': 1},
                                                                       {'id_session_type': 2}]}}
            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="New session type association OK")

            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 2)  # Everything was added

            json_data = {'project': {'id_project': 1, 'sessiontypes': [{'id_session_type': 1}]}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Remove 1 type")

            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            json_data = {'project': {'id_project': 1, 'sessiontypes': [{'id_session_type': 1},
                                                                       {'id_session_type': 2},
                                                                       {'id_session_type': 3},
                                                                       {'id_session_type': 4},
                                                                       {'id_session_type': 5}]}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Back to initial state")

    def test_post_session_type_project_and_delete(self):
        with self._flask_app.app_context():
            # Device-Project update
            json_data = {'session_type_project': {}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Badly formatted request")

            json_data = {'session_type_project': {'id_project': 1}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Badly formatted request")

            json_data = {'session_type_project': {'id_project': 1, 'id_session_type': 1}}
            response = self._post_with_user_http_auth(username='user', password='user', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

            json_data = {'session_type_project': {'id_project': 1, 'id_session_type': 6}}
            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Add new association not OK - type not part of the site")

            json_data = {'session_type_project': {'id_project': 2, 'id_session_type': 3}}
            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Add new association OK")

            params = {'id_project': 2}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json

            current_id = None
            for dp in json_data:
                if dp['id_session_type'] == 3:
                    current_id = dp['id_session_type_project']
                    break
            self.assertFalse(current_id is None)

            response = self._delete_with_user_http_auth(username='user', password='user', params='id='+str(current_id),
                                                        client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Delete denied")

            response = self._delete_with_user_http_auth(username='siteadmin', password='siteadmin',
                                                        params='id='+str(current_id), client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Delete OK")

            params = {'id_project': 2}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_session_type_project'))
        self.assertTrue(json_data.__contains__('id_session_type'))
        self.assertTrue(json_data.__contains__('id_project'))

        if not minimal:
            self.assertTrue(json_data.__contains__('session_type_name'))
            self.assertTrue(json_data.__contains__('project_name'))
        else:
            self.assertFalse(json_data.__contains__('session_type_name'))
            self.assertFalse(json_data.__contains__('project_name'))
