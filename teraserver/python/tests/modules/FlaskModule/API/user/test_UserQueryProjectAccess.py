from BaseUserAPITest import BaseUserAPITest


class UserQueryProjectAccessTest(BaseUserAPITest):
    test_endpoint = '/api/user/projectaccess'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_no_auth(self):
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

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(400, response.status_code)

    def test_query_specific_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 2})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['project_access_role'], 'admin')
                self.assertEqual(data_item['project_access_inherited'], True)

    def test_query_specific_user_with_sites(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 2, 'with_sites': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['project_access_role'], 'admin')
                self.assertEqual(data_item['id_site'], 1)

    def test_query_specific_user_admins(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 2, 'admins': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['project_access_role'], 'admin')

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 3, 'admins': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

    def test_query_specific_user_admins_with_sites(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 2, 'admins': True, 'with_sites': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['project_access_role'], 'admin')
                self.assertEqual(data_item['id_site'], 1)

    def test_query_specific_user_group(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['project_access_role'], 'user')

    def test_query_specific_user_group_with_sites(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 1, 'with_sites': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['project_access_role'], 'user')
                self.assertEqual(data_item['id_site'], 1)

    def test_query_specific_user_group_admins(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 1, 'admins': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

    def test_query_specific_user_group_admins_with_sites(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 3, 'admins': True, 'with_sites': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['project_access_role'], 'admin')
                self.assertEqual(data_item['id_site'], 1)

    def test_query_specific_user_group_by_users(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', 
                                                     params={'id_user_group': 1, 'by_users': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['project_access_role'], 'user')
                self.assertEqual(data_item['project_access_inherited'], False)

    def test_query_specific_user_group_by_users_with_sites(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 3, 'by_users': True, 'with_sites': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['project_access_role'], 'admin')
                self.assertEqual(data_item['project_access_inherited'], True)
                self.assertEqual(data_item['id_site'], 1)

    def test_query_specific_user_group_by_users_with_projects(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 3, 'by_users': True, 'with_empty': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(6, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                if data_item['id_project'] != 3:
                    self.assertEqual(data_item['project_access_role'], 'admin')
                    self.assertEqual(data_item['project_access_inherited'], True)
                else:
                    self.assertEqual(data_item['project_access_role'], None)

    def test_query_specific_user_group_by_users_with_projects_with_sites(self):
        with self._flask_app.app_context():
            params = {'id_user_group': 3, 'by_users': True, 'with_empty': True, 'with_sites': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(6, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_site'))
                if data_item['id_project'] != 3:
                    self.assertEqual(data_item['project_access_role'], 'admin')
                    self.assertEqual(data_item['project_access_inherited'], True)
                else:
                    self.assertEqual(data_item['project_access_role'], None)

    def test_query_specific_user_group_by_users_with_projects_admins(self):
        with self._flask_app.app_context():
            params = {'id_user_group': 2, 'by_users': True, 'with_empty': True, 'admins': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                if data_item['id_project'] == 1:
                    self.assertEqual(data_item['project_access_role'], 'admin')
                else:
                    self.assertEqual(data_item['project_access_role'], None)

    def test_query_specific_user_group_by_users_with_projects_admins_with_sites(self):
        with self._flask_app.app_context():
            params = {'id_user_group': 4, 'by_users': True, 'with_empty': True, 'admins': True, 'with_sites': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', 
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_site'))
                if data_item['id_project'] != 3:
                    self.assertEqual(data_item['project_access_role'], 'admin')
                else:
                    self.assertEqual(data_item['project_access_role'], None)

    def test_query_specific_user_group_with_projects_admins(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 3, 'with_empty': True, 'admins': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                if data_item['id_project'] != 3:
                    self.assertEqual(data_item['project_access_role'], 'admin')
                else:
                    self.assertEqual(data_item['project_access_role'], None)

    def test_query_specific_user_group_with_projects_admins_with_sites(self):
        with self._flask_app.app_context():
            params = {'id_user_group': 2, 'with_empty': True, 'admins': True, 'with_sites': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_site'))
                if data_item['id_project'] == 1:
                    self.assertEqual(data_item['project_access_role'], 'admin')
                else:
                    self.assertEqual(data_item['project_access_role'], None)

    def test_query_specific_project(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', 
                                                     params={'id_project': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user_group'))
                if data_item['id_user_group'] == 3 or data_item['id_user_group'] == 2:
                    self.assertEqual(data_item['project_access_role'], 'admin')
                else:
                    self.assertEqual(data_item['project_access_role'], 'user')

    def test_query_specific_project_with_sites(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 2, 'with_sites': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user_group'))
                self.assertEqual(data_item['id_site'], 1)
                if data_item['id_user_group'] == 3:
                    self.assertEqual(data_item['project_access_role'], 'admin')
                else:
                    self.assertEqual(data_item['project_access_role'], 'user')

    def test_query_specific_project_admins(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1, 'admins': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user_group'))
                self.assertEqual(data_item['project_access_role'], 'admin')

    def test_query_specific_project_admins_with_sites(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 2, 'admins': True, 'with_sites': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user_group'))
                self.assertEqual(data_item['id_site'], 1)
                self.assertEqual(data_item['project_access_role'], 'admin')

    def test_query_specific_project_by_users(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1, 'by_users': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))

    def test_query_specific_project_by_users_with_sites(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1, 'by_users': True, 'with_sites': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))
                self.assertEqual(data_item['id_site'], 1)

    def test_query_specific_project_by_users_admins(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1, 'by_users': True, 'admins': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))
                self.assertEqual(data_item['project_access_role'], 'admin')

    def test_query_specific_project_by_users_admins_with_sites(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'by_users': True, 'admins': True, 'with_sites': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)

            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))
                self.assertEqual(data_item['project_access_role'], 'admin')
                self.assertEqual(data_item['id_site'], 1)

    def test_query_specific_project_by_users_with_user_groups(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 2, 'by_users': True, 'with_empty': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))
                if data_item['id_user'] == 2 or data_item['id_user'] == 4:
                    self.assertEqual(data_item['project_access_role'], 'admin')
                    self.assertEqual(data_item['project_access_inherited'], True)
                elif data_item['id_user'] == 5:
                    self.assertEqual(data_item['project_access_role'], None)
                    self.assertEqual(data_item['project_access_inherited'], None)
                else:
                    self.assertEqual(data_item['project_access_role'], 'user')
                    self.assertEqual(data_item['project_access_inherited'], False)

    def test_query_specific_project_by_users_with_user_groups_with_sites(self):
        with self._flask_app.app_context():
            params = {'id_project': 2, 'by_users': True, 'with_empty': True, 'with_sites': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)

            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))
                self.assertEqual(data_item['id_site'], 1)
                if data_item['id_user'] == 2 or data_item['id_user'] == 4:
                    self.assertEqual(data_item['project_access_role'], 'admin')
                    self.assertEqual(data_item['project_access_inherited'], True)
                elif data_item['id_user'] == 5:
                    self.assertEqual(data_item['project_access_role'], None)
                    self.assertEqual(data_item['project_access_inherited'], None)
                else:
                    self.assertEqual(data_item['project_access_role'], 'user')
                    self.assertEqual(data_item['project_access_inherited'], False)

    def test_query_specific_project_by_users_with_user_groups_admins(self):
        with self._flask_app.app_context():
            params = {'id_project': 2, 'by_users': True, 'with_empty': True, 'admins': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))
                if data_item['id_user'] == 5:
                    self.assertEqual(data_item['project_access_role'], None)
                    self.assertEqual(data_item['project_access_inherited'], None)
                else:
                    self.assertNotEqual(data_item['project_access_role'], None)
                    self.assertNotEqual(data_item['project_access_inherited'], None)

    def test_query_specific_project_by_users_with_user_groups_admins_with_sites(self):
        with self._flask_app.app_context():
            params = {'id_project': 2, 'by_users': True, 'with_empty': True, 'admins': True, 'with_sites': True}

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', 
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))
                self.assertEqual(data_item['id_site'], 1)
                if data_item['id_user'] == 5:
                    self.assertEqual(data_item['project_access_role'], None)
                    self.assertEqual(data_item['project_access_inherited'], None)
                else:
                    self.assertNotEqual(data_item['project_access_role'], None)
                    self.assertNotEqual(data_item['project_access_inherited'], None)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                'project_access': {
                    'project_access_role': 'admin'
                }
            }

            response = self._post_with_user_http_auth(self.test_client,  username='user', password='user',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_usergroup")  # Missing id_usergroup

            json_data['project_access']['id_user_group'] = str(4)
            response = self._post_with_user_http_auth(self.test_client,  username='user', password='user',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_site")  # Missing id_site

            json_data['project_access']['id_project'] = str(3)
            response = self._post_with_user_http_auth(self.test_client,  username='user4', password='user4',
                                                      json=json_data)

            self.assertEqual(403, response.status_code, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

            json_data = response.json[0]
            self._checkJson(json_data)
            current_id = json_data['id_project_access']
            self.assertEqual(json_data['project_access_role'], 'admin')

            json_data = {
                'project_access': {
                    'project_access_role': 'user',
                    'id_user_group': 4,
                    'id_project': 3
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post update")
            json_data = response.json[0]
            self._checkJson(json_data)
            self.assertEqual(json_data['project_access_role'], 'user')

            # Delete
            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('project_access_role'))
