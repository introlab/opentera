from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest


class UserQuerySiteAccessTest(BaseUserAPITest):
    test_endpoint = '/api/user/siteaccess'

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
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['site_access_role'], 'admin')

    def test_query_specific_user_admins(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 2, 'admins': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['site_access_role'], 'admin')

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 3, 'admins': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

    def test_query_specific_user_group(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(1, data_item['id_site'])
                self.assertEqual(data_item['site_access_role'], 'user')
                self.assertTrue(data_item['site_access_inherited'])

    def test_query_specific_user_group_admins(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 1, 'admins': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

    def test_query_specific_user_group_by_users(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 2, 'by_users': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['site_access_role'], 'user')
                self.assertTrue(data_item['site_access_inherited'])

    def test_query_specific_user_group_by_users_with_sites(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 3, 'by_users': True, 'with_empty': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                if data_item['id_site'] == 1:
                    self.assertEqual(data_item['site_access_role'], 'admin')
                    self.assertFalse(data_item['site_access_inherited'])
                else:
                    self.assertIsNone(data_item['site_access_role'])

    def test_query_specific_user_group_by_users_with_sites_admins(self):
        with self._flask_app.app_context():
            params = {'id_user_group': 2, 'by_users': True, 'with_empty': True, 'admins': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertIsNone(data_item['site_access_role'])

    def test_query_specific_user_group_with_sites_admins(self):
        with self._flask_app.app_context():
            params = {'id_user_group': 3, 'with_empty': True, 'admins': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)

            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                if data_item['id_site'] == 1:
                    self.assertEqual(data_item['site_access_role'], 'admin')
                else:
                    self.assertIsNone(data_item['site_access_role'])

    def test_query_specific_site(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user_group'))
                if "site_access_inherited" in data_item:
                    self.assertEqual(data_item['site_access_role'], 'user')
                    self.assertTrue(data_item['site_access_inherited'])

    def test_query_specific_site_admins(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1, 'admins': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user_group'))
                self.assertEqual(data_item['site_access_role'], 'admin')

    def test_query_specific_site_by_users(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1, 'by_users': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreaterEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))

    def test_query_specific_site_by_users_admins(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'by_users': True, 'admins': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))
                self.assertTrue(data_item.__contains__('user_name'))
                self.assertTrue(data_item.__contains__('user_enabled'))
                self.assertEqual(data_item['site_access_role'], 'admin')

    def test_query_specific_site_by_users_with_user_groups(self):
        with self._flask_app.app_context():
            params = {'id_site': 2, 'by_users': True, 'with_empty': True, 'with_usergroups': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreaterEqual(4, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))
                self.assertIsNone(data_item['site_access_role'])
                self.assertIsNone(data_item['site_access_inherited'])
                self.assertTrue(data_item.__contains__('user_groups'))

    def test_query_specific_site_by_users_with_user_groups_admins(self):
        with self._flask_app.app_context():
            params = {'id_site': 2, 'by_users': True, 'with_empty': True, 'with_usergroups': True, 'admins': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreaterEqual(len(response.json), 4)

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_user'))
                self.assertIsNone(data_item['site_access_role'])
                self.assertTrue(data_item.__contains__('user_groups'))

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                'site_access': {
                    'site_access_role': 'admin'
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_usergroup")  # Missing id_usergroup

            json_data['site_access']['id_user_group'] = 2
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_site")  # Missing id_site

            json_data['site_access']['id_site'] = 1
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            # Forbidden for that user to post that
            self.assertEqual(403, response.status_code, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post new")
            self.assertGreater(len(response.json), 0)
            json_data = response.json[0]
            self._checkJson(json_data)
            self.assertEqual(json_data['site_access_role'], 'admin')

            json_data = {
                'site_access': {
                    'site_access_role': 'user',
                    'id_user_group': 2,
                    'id_site': 1
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post update")
            # Setting user role, but that usergroup already inherits that access, so no return value!
            self.assertEqual(0, len(response.json))

            json_data = {
                'site_access': {
                    'site_access_role': 'admin',
                    'id_user_group': 5,  # No access usergroup
                    'id_site': 1
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post new, take 2")
            self.assertGreater(len(response.json), 0)
            json_data = response.json[0]
            self._checkJson(json_data)
            current_id = json_data['id_site_access']
            self.assertEqual(json_data['site_access_role'], 'admin')

            json_data = {
                'site_access': {
                    'site_access_role': 'user',
                    'id_user_group': 5,
                    'id_site': 1
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post update, take 2")
            self.assertGreater(len(response.json), 0)
            json_data = response.json[0]
            current_id2 = json_data['id_site_access']
            self._checkJson(json_data)
            self.assertEqual(json_data['site_access_role'], 'user')

            # Delete
            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(200, response.status_code, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('site_access_role'))
