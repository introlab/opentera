from BaseUserAPITest import BaseUserAPITest


class UserQuerySessionTypeSitesTest(BaseUserAPITest):
    test_endpoint = '/api/user/sessiontypes/sites'

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

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(400, response.status_code)

    def test_query_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user')
            self.assertEqual(400, response.status_code)

    def test_query_site_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 10}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 0)
    
            params = {'id_site': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 1)
    
            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_site_with_session_types_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'with_session_type': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(5, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_type_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 30}  # Invalid
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_session_type': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_type_with_site_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 3, 'with_sites': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'list': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(5, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_site_as_user(self):
        with self._flask_app.app_context():
            params = {'id_site': 2}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(5, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_site_with_session_types_as_user(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'with_session_type': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(5, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_type_as_user(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 30}  # Invalid
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_session_type': 4}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_session_type': 2}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_type_with_sites_as_user(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 1, 'with_sites': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 1, 'list': 1}

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_post_session_type(self):
        with self._flask_app.app_context():
            json_data = {}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing everything")  # Missing

            # Update
            json_data = {'session_type': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_session_type")

            json_data = {'session_type': {'id_session_type': 4}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing sites")

            json_data = {'session_type': {'id_session_type': 4, 'sites': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only site admins can change things here")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove from all accessible sites OK")

            params = {'id_session_type': 4}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))  # One should remain in the "top secret" site

            json_data = {'session_type': {'id_session_type': 4, 'sites': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove from all accessible sites OK")

            params = {'id_session_type': 4}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # None remaining now

            json_data = {'session_type': {'id_session_type': 4, 'sites': [{'id_site': 1},
                                                                          {'id_site': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to site 2")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="All posted ok")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))  # Everything was added

            json_data = {'session_type': {'id_session_type': 4, 'sites': [{'id_site': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove one site")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            json_data = {'session_type': {'id_session_type': 4, 'sites': [{'id_site': 1},
                                                                          {'id_site': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all sites OK")

            # Recreate default associations - projects
            json_data = {'session_type_project': [{'id_session_type': 4, 'id_project': 1}]}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data, endpoint='/api/user/sessiontypes/projects')
            self.assertEqual(200, response.status_code)

    def test_post_site(self):
        with self._flask_app.app_context():
            json_data = {'site': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_site")

            json_data = {'site': {'id_site': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing services")

            json_data = {'site': {'id_site': 1, 'sessiontypes': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only site admins can change things here")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove all services OK")

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            json_data = {'site': {'id_site': 1, 'sessiontypes': [{'id_session_type': 1},
                                                                 {'id_session_type': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all session types OK")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))  # Everything was added

            json_data = {'site': {'id_site': 1, 'sessiontypes': [{'id_session_type': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove 1 session type")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            json_data = {'site': {'id_site': 1, 'sessiontypes': [{'id_session_type': 1},
                                                                 {'id_session_type': 2},
                                                                 {'id_session_type': 3},
                                                                 {'id_session_type': 4},
                                                                 {'id_session_type': 5}
                                                                 ]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Back to defaults")

            # Recreate default associations - projects
            json_data = {'session_type_project': [{'id_session_type': 1, 'id_project': 1},
                                                  {'id_session_type': 2, 'id_project': 1},
                                                  {'id_session_type': 3, 'id_project': 1},
                                                  {'id_session_type': 4, 'id_project': 1},
                                                  {'id_session_type': 5, 'id_project': 1}]}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data, endpoint='/api/user/sessiontypes/projects')
            self.assertEqual(200, response.status_code)

    def test_post_session_type_site_and_delete(self):
        with self._flask_app.app_context():
            json_data = {'session_type_site': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'session_type_site': {'id_site': 2}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'session_type_site': {'id_site': 2, 'id_session_type': 3}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only site admins can change things here")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Not site admin either for that site")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add new association OK")

            params = {'id_site': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))

            current_id = None
            for sp in response.json:
                if sp['id_session_type'] == 3:
                    current_id = sp['id_session_type_site']
                    break
            self.assertFalse(current_id is None)
            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user', password='user',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete still denied")

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(200, response.status_code, msg="Delete OK")

            params = {'id_site': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))  # Back to initial state!

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_session_type_site'))
        self.assertTrue(json_data.__contains__('id_session_type'))
        self.assertTrue(json_data.__contains__('id_site'))

        if not minimal:
            self.assertTrue(json_data.__contains__('session_type_name'))
            self.assertTrue(json_data.__contains__('site_name'))
        else:
            self.assertFalse(json_data.__contains__('session_type_name'))
            self.assertFalse(json_data.__contains__('site_name'))
