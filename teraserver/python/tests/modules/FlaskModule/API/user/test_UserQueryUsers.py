from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import datetime


class UserQueryUsersTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/users'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_auth(self):
        response = self._request_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_post_no_auth(self):
        response = self._post_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_delete_no_auth(self):
        response = self._delete_with_no_auth(id_to_del=0)
        self.assertEqual(response.status_code, 401)

    def test_query_no_params_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 6)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="")
        json_data = response.json()
        self.assertEqual(len(json_data), 3)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_list_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="list=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_user_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=6")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        user_uuid = None
        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user'], 6)
            user_uuid = data_item['user_uuid']

        response = self._request_with_http_auth(username='admin', password='admin', payload="user_uuid=" + user_uuid)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['user_uuid'], user_uuid)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=6&list=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=4"
                                                                                            "&with_usergroups=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('user_user_groups'))
            self.assertEqual(len(data_item["user_user_groups"]), 2)

    def test_query_specific_user_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="id_user=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        response = self._request_with_http_auth(username='user', password='user', payload="id_user=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        user_uuid = None
        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user'], 4)
            user_uuid = data_item['user_uuid']

        response = self._request_with_http_auth(username='user', password='user', payload="user_uuid=" + user_uuid)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['user_uuid'], user_uuid)

    def test_query_specific_usergroup_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user_group=3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user_group=3&list=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user_group=3"
                                                                                            "&with_usergroups=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('user_user_groups'))

    def test_query_specific_usergroup_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="id_user_group=1")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_specific_project(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_project=1")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 5)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

        response = self._request_with_http_auth(username='user4', password='user4', payload="id_project=1")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

    def test_query_with_status(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="with_status=1")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 6)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('user_online'))
            self.assertTrue(data_item.__contains__('user_busy'))

        response = self._request_with_http_auth(username='admin', password='admin', payload="with_status=1&list=1")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 6)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)
            self.assertTrue(data_item.__contains__('user_online'))
            self.assertTrue(data_item.__contains__('user_busy'))

    def test_query_specific_username_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="username=user3")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['user_username'], 'user3')

        response = self._request_with_http_auth(username='admin', password='admin', payload="username=user3&list=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

        response = self._request_with_http_auth(username='admin', password='admin', payload="username=user3"
                                                                                            "&with_usergroups=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('user_user_groups'))
            self.assertEqual(data_item['user_username'], 'user3')

    def test_query_specific_username_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="username=user4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        response = self._request_with_http_auth(username='user', password='user', payload="username=user2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['user_username'], 'user2')

    def test_query_self(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="self=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['user_username'], 'admin')
            self.assertTrue(data_item.__contains__('projects'))
            self.assertTrue(data_item.__contains__('sites'))

        response = self._request_with_http_auth(username='user4', password='user4', payload="self=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['user_username'], 'user4')
            self.assertTrue(data_item.__contains__('projects'))
            self.assertTrue(data_item.__contains__('sites'))

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'user': {
                'user_username': 'admin',
                'user_enabled': True,
                'user_firstname': 'Test',
                'user_lastname': 'Test',
                'user_profile': ''
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_user")

        json_data['user']['id_user'] = 0
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing fields")

        json_data['user']['user_password'] = ''
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Missing usergroups")

        json_data['user']['user_user_groups'] = [{'id_user_group': 3}, {'id_user_group': 5}]
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="No access to user groups!")

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Invalid password")

        json_data['user']['user_password'] = 'testtest'
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 409, msg="Username unavailable")

        json_data['user']['user_username'] = 'selftest'
        response = self._post_with_http_auth(username='user4', password='user4', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

        json_data = response.json()[0]
        self._checkJson(json_data)
        current_id = json_data['id_user']

        json_data = {
            'user': {
                'id_user': current_id,
                'user_enabled': False,
                'user_user_groups': [{'id_user_group': 3}, {'id_user_group': 1}]
            }
        }

        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Changed user groups")

        # Check that the untouched user group is still there
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_user=" + str(current_id),
                                                endpoint='/api/user/users/usergroups')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        reply_data = response.json()
        self.assertEqual(len(reply_data), 3)

        json_data['user']['user_user_groups'] = [{'id_user_group': 3}]
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Changed user groups")

        # Check that the untouched user group is still there
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_user=" + str(current_id),
                                                endpoint='/api/user/users/usergroups')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        reply_data = response.json()
        self.assertEqual(len(reply_data), 2)

        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="User can't modify that user")

        json_data['user']['user_username'] = 'selftest2'
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Can't change user_username")

        del json_data['user']['user_username']
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update OK")
        json_reply = response.json()[0]
        self._checkJson(json_reply)
        self.assertEqual(json_reply['user_enabled'], False)

        response = self._delete_with_http_auth(username='user4', password='user4', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='siteadmin', password='siteadmin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Deleted groups, but not user = OK")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Deleted user completely")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_user'))
        self.assertTrue(json_data.__contains__('user_enabled'))
        self.assertTrue(json_data.__contains__('user_firstname'))
        self.assertTrue(json_data.__contains__('user_lastname'))
        self.assertTrue(json_data.__contains__('user_name'))
        self.assertTrue(json_data.__contains__('user_uuid'))

        if minimal:
            self.assertFalse(json_data.__contains__('user_email'))
            self.assertFalse(json_data.__contains__('user_lastonline'))
            self.assertFalse(json_data.__contains__('user_notes'))
            self.assertFalse(json_data.__contains__('user_profile'))
            self.assertFalse(json_data.__contains__('user_username'))
        else:
            self.assertTrue(json_data.__contains__('user_email'))
            self.assertTrue(json_data.__contains__('user_lastonline'))
            self.assertTrue(json_data.__contains__('user_notes'))
            self.assertTrue(json_data.__contains__('user_profile'))
            self.assertTrue(json_data.__contains__('user_username'))
