from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import datetime


class UserQueryUserUserGroupsTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/users/usergroups'

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
        self.assertEqual(response.status_code, 400)

    def test_query_specific_usergroup_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user_group=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user_group'], 1)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user_group=1"
                                                                                            "&with_empty=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 5)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            if data_item['id_user_group'] != 1:
                self.assertEqual(data_item['id_user_group'], None)
                self.assertNotEqual(data_item['id_user'], None)
                self.assertNotEqual(data_item['user_fullname'], None)

    def test_query_specific_usergroup_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="id_user_group=4")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user_group'], 4)

    def test_query_specific_usergroup_list_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="id_user_group=4&list=1")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)
            self.assertEqual(data_item['id_user_group'], 4)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user_group=4"
                                                                                            "&list=1"
                                                                                            "&with_empty=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 5)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)
            if data_item['id_user_group'] != 4:
                self.assertEqual(data_item['id_user_group'], None)
                self.assertNotEqual(data_item['id_user'], None)
                self.assertFalse(data_item.__contains__('user_fullname'))

    def test_query_specific_user_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user'], 4)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=4&with_empty=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 5)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            if data_item['id_user'] != 4:
                self.assertEqual(data_item['id_user'], None)
                self.assertNotEqual(data_item['id_user_group'], None)
                self.assertEqual(data_item['user_fullname'], None)
                self.assertNotEqual(data_item['user_group_name'], None)

    def test_query_specific_user_list_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=4&list=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)
            self.assertEqual(data_item['id_user'], 4)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=4&list=1&"
                                                                                            "with_empty=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 5)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)
            if data_item['id_user'] != 4:
                self.assertEqual(data_item['id_user'], None)
                self.assertNotEqual(data_item['id_user_group'], None)
                self.assertFalse(data_item.__contains__('user_group_name'))

    def test_query_specific_user_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="id_user=1")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'user_user_group': {
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_user")  # Missing id_user

        json_data['user_user_group']['id_user'] = 1
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_user_group")

        json_data['user_user_group']['id_user_group'] = 2
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="No groups to super admins!")

        json_data['user_user_group']['id_user'] = 2
        response = self._post_with_http_auth(username='user4', password='user4', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

        json_data = response.json()[0]
        self._checkJson(json_data, minimal=True)
        current_id = json_data['id_user_user_group']

        json_data = {
            'user_user_group': {
                'id_user': 2,
                'id_user_group': 2
            }
        }
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update OK")
        json_reply = response.json()[0]
        self._checkJson(json_reply, minimal=True)
        self.assertEqual(json_reply['id_user_user_group'], current_id)

        response = self._delete_with_http_auth(username='user4', password='user4', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

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
