from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUserGroup import TeraUserGroup
from opentera.db.models.TeraUser import TeraUser


class UserQueryUserUserGroupsTest(BaseUserAPITest):
    test_endpoint = '/api/user/users/usergroups'

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
            response = self._get_with_user_http_auth(username='admin', password='admin', client=self.test_client)
            self.assertEqual(response.status_code, 400, msg='At least one id required')

    def test_query_specific_usergroup_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_user_group=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_user_group'], 1)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_user_group=1&with_empty=true")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            target_count = TeraUserGroup.get_count()
            self.assertEqual(len(json_data), target_count)

            for data_item in json_data:
                self._checkJson(json_data=data_item)
                if data_item['id_user_group'] != 1:
                    self.assertEqual(data_item['id_user_group'], None)
                    self.assertNotEqual(data_item['id_user'], None)
                    self.assertNotEqual(data_item['user_fullname'], None)

    def test_query_specific_usergroup_as_user(self):
        response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                 params="id_user_group=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                 params="id_user_group=4")
        self.assertEqual(response.status_code, 200)
        json_data = response.json
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user_group'], 4)

    def test_query_specific_usergroup_lists(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params="id_user_group=4&list=1")
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)
                self.assertEqual(data_item['id_user_group'], 4)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_user_group=4&list=1&with_empty=true")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            target_count = TeraUserGroup.get_count()
            self.assertEqual(len(json_data), target_count)

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)
                if data_item['id_user_group'] != 4:
                    self.assertEqual(data_item['id_user_group'], None)
                    self.assertNotEqual(data_item['id_user'], None)
                    self.assertFalse(data_item.__contains__('user_fullname'))

    def test_query_specific_user_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_user=4")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            target_user_groups = TeraUser.get_user_by_id(4).user_user_groups
            user_groups_ids = [ug.id_user_group for ug in target_user_groups]
            self.assertEqual(len(json_data), len(target_user_groups))

            for data_item in json_data:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_user'], 4)
                self.assertTrue(data_item['id_user_group'] in user_groups_ids)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_user=4&with_empty=true")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            target_count = TeraUserGroup.get_count()
            self.assertEqual(len(json_data), target_count)

            for data_item in json_data:
                self._checkJson(json_data=data_item)
                if data_item['id_user'] != 4:
                    self.assertEqual(data_item['id_user'], None)
                    self.assertNotEqual(data_item['id_user_group'], None)
                    self.assertEqual(data_item['user_fullname'], None)
                    self.assertNotEqual(data_item['user_group_name'], None)

    def test_query_specific_user_list_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_user=4&list=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            target_user_groups = TeraUser.get_user_by_id(4).user_user_groups
            self.assertEqual(len(json_data), len(target_user_groups))

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)
                self.assertEqual(data_item['id_user'], 4)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_user=4&list=1&with_empty=true")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            target_count = TeraUserGroup.get_count()
            self.assertEqual(len(json_data), target_count)

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)
                if data_item['id_user'] != 4:
                    self.assertEqual(data_item['id_user'], None)
                    self.assertNotEqual(data_item['id_user_group'], None)
                    self.assertFalse(data_item.__contains__('user_group_name'))

    def test_query_specific_user_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params="id_user=1")
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            user3 = TeraUser.get_user_by_username('user3')
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params="id_user=" + str(user3.id_user))
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = len(user3.user_user_groups)
            self.assertEqual(len(json_data), target_count)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                'id_user_group': 2,
                'id_user': 1
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing user user group")

            json_data = {
                'user_user_group': {
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing id_user")

            json_data['user_user_group']['id_user'] = 1
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing id_user_group")

            json_data['user_user_group']['id_user_group'] = 2
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=json_data)
            self.assertEqual(response.status_code, 400, msg="No groups to super admins!")

            json_data['user_user_group']['id_user'] = 2
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4', json=json_data)
            self.assertEqual(response.status_code, 403, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

            json_data = response.json[0]
            self._checkJson(json_data, minimal=True)
            current_id = json_data['id_user_user_group']

            json_data = {
                'user_user_group': {
                    'id_user': 2,
                    'id_user_group': 2
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post update OK")
            json_reply = response.json[0]
            self._checkJson(json_reply, minimal=True)
            self.assertEqual(json_reply['id_user_user_group'], current_id)  # No change since the same id as before

            json_data = {
                'user_user_group': {
                    'id_user_user_group': current_id,
                    'id_user': 2,
                    'id_user_group': 3
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post update OK")
            json_reply = response.json[0]
            self._checkJson(json_reply, minimal=True)
            self.assertNotEqual(json_reply['id_user_user_group'], current_id)  # New relationship was created
            current_id2 = json_reply['id_user_user_group']
            user: TeraUser = TeraUser.get_user_by_id(2)
            usergroup_ids = [ug.id_user_group for ug in user.user_user_groups]
            self.assertTrue(3 in usergroup_ids)
            self.assertTrue(2 in usergroup_ids)

            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params={'id': current_id})
            self.assertEqual(response.status_code, 403, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(response.status_code, 200, msg="Delete OK")
            usergroup_ids = [ug.id_user_group for ug in user.user_user_groups]
            self.assertFalse(2 in usergroup_ids)
            self.assertTrue(3 in usergroup_ids)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id2})
            self.assertEqual(response.status_code, 200, msg="Delete OK")
            usergroup_ids = [ug.id_user_group for ug in user.user_user_groups]
            self.assertFalse(2 in usergroup_ids)
            self.assertFalse(3 in usergroup_ids)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_user_group'))
        self.assertTrue(json_data.__contains__('id_user'))
        self.assertTrue(json_data.__contains__('id_user_user_group'))

        if minimal:
            self.assertFalse(json_data.__contains__('user_fullname'))
            self.assertFalse(json_data.__contains__('user_group_name'))
        else:
            self.assertTrue(json_data.__contains__('user_fullname'))
            self.assertTrue(json_data.__contains__('user_group_name'))
