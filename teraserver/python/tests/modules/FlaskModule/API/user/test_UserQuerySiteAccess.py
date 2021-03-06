from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import datetime


class UserQuerySiteAccessTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/siteaccess'

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

    def test_query_specific_user(self):

        # Query specific user
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_user=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['site_access_role'], 'admin')

    def test_query_specific_user_admins(self):

        # Query specific user
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_user=2&admins=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['site_access_role'], 'admin')

        response = self._request_with_http_auth(username='admin', password='admin', payload='id_user=3&admins=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

    def test_query_specific_user_group(self):
        # Query specific user_group
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_user_group=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_site'], 1)
            self.assertEqual(data_item['site_access_role'], 'user')
            self.assertEqual(data_item['site_access_inherited'], True)

    def test_query_specific_user_group_admins(self):
        # Query specific user_group
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_user_group=1'
                                                                                            '&admins=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

    def test_query_specific_user_group_by_users(self):
        # Now query with by_user flags
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_user_group=2&by_users='
                                                                                            'true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['site_access_role'], 'user')
            self.assertEqual(data_item['site_access_inherited'], True)

    def test_query_specific_user_group_by_users_with_sites(self):
        # Now query with by_user flags
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload='id_user_group=3&by_users='
                                                        'true&with_empty=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 4)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            if data_item['id_site'] == 1:
                self.assertEqual(data_item['site_access_role'], 'admin')
                self.assertEqual(data_item['site_access_inherited'], False)
            else:
                self.assertEqual(data_item['site_access_role'], None)

    def test_query_specific_user_group_by_users_with_sites_admins(self):
        # Now query with by_user flags
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload='id_user_group=2&by_users='
                                                        'true&with_empty=true&admins=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['site_access_role'], None)

    def test_query_specific_user_group_with_sites_admins(self):
        # Now query with by_user flags
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload='id_user_group=3&with_empty=true&admins=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            if data_item['id_site'] == 1:
                self.assertEqual(data_item['site_access_role'], 'admin')
            else:
                self.assertEqual(data_item['site_access_role'], None)

    def test_query_specific_site(self):
        # Query specific site
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_site=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 4)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('id_user_group'))
            if "site_access_inherited" in data_item:
                self.assertEqual(data_item['site_access_role'], 'user')
                self.assertEqual(data_item['site_access_inherited'], True)

    def test_query_specific_site_admins(self):
        # Query specific site
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_site=1&admins=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('id_user_group'))
            self.assertEqual(data_item['site_access_role'], 'admin')

    def test_query_specific_site_by_users(self):
        # Query specific site
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_site=1&by_users=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreaterEqual(len(json_data), 4)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('id_user'))

    def test_query_specific_site_by_users_admins(self):
        # Query specific site
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_site=1&by_users=true'
                                                                                            '&admins=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('id_user'))
            self.assertTrue(data_item.__contains__('user_name'))
            self.assertTrue(data_item.__contains__('user_enabled'))
            self.assertEqual(data_item['site_access_role'], 'admin')

    def test_query_specific_site_by_users_with_user_groups(self):
        # Query specific site
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_site=2&by_users=true'
                                                                                            '&with_empty=true'
                                                                                            '&with_usergroups=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreaterEqual(len(json_data), 4)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('id_user'))
            self.assertEqual(data_item['site_access_role'], None)
            self.assertEqual(data_item['site_access_inherited'], None)
            self.assertTrue(data_item.__contains__('user_groups'))

    def test_query_specific_site_by_users_with_user_groups_admins(self):
        # Query specific site
        response = self._request_with_http_auth(username='admin', password='admin', payload='id_site=2&by_users=true'
                                                                                            '&with_empty=true'
                                                                                            '&with_usergroups=true'
                                                                                            '&admins=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreaterEqual(len(json_data), 4)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('id_user'))
            self.assertEqual(data_item['site_access_role'], None)
            self.assertTrue(data_item.__contains__('user_groups'))

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'site_access': {
                'site_access_role': 'admin'
            }
        }

        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_usergroup")  # Missing id_usergroup

        json_data['site_access']['id_user_group'] = str(2)
        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_site")  # Missing id_site

        json_data['site_access']['id_site'] = str(1)
        response = self._post_with_http_auth(username='user4', password='user4', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

        json_data = response.json()[0]
        self._checkJson(json_data)
        current_id = json_data['id_site_access']
        self.assertEqual(json_data['site_access_role'], 'admin')

        json_data = {
            'site_access': {
                'site_access_role': 'user',
                'id_user_group': 2,
                'id_site': 1
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update")
        # Setting user role, but that usergroup already inherits that access, so no return value!
        self.assertEqual(len(response.json()), 0)

        json_data = {
            'site_access': {
                'site_access_role': 'admin',
                'id_user_group': 5, # No access usergroup
                'id_site': 1
            }
        }
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new, take 2")

        json_data = response.json()[0]
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
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update, take 2")
        json_data = response.json()[0]
        self._checkJson(json_data)
        self.assertEqual(json_data['site_access_role'], 'user')

        # Delete
        response = self._delete_with_http_auth(username='user4', password='user4', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('site_access_role'))
