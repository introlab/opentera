from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import datetime


class UserQueryUserGroupsTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/usergroups'

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
        self.assertEqual(len(json_data), 5)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="")
        json_data = response.json()
        self.assertGreater(len(json_data), 1)

    def test_query_list_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="list=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 5)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_usergroup_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user_group=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user_group'], 1)

    def test_query_usergroup_for_specific_site(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_site=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 4)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_site=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

    def test_query_specific_usergroup_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="id_user_group=4")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_specific_user_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(len(data_item['user_group_projects_access']), 2)
            for project_item in data_item['user_group_projects_access']:
                self.assertEqual(project_item['project_access_role'], 'admin')
            self.assertEqual(len(data_item['user_group_sites_access']), 1)
            for site_item in data_item['user_group_sites_access']:
                self.assertEqual(site_item['site_access_role'], 'admin')

    def test_query_specific_user_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="id_user=2")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        # for data_item in json_data:
        #     self._checkJson(json_data=data_item)

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'user_group': {
                    'user_group_name': 'Test'
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_user_group")  # Missing id_user_group

        json_data['user_group']['id_user_group'] = 0
        response = self._post_with_http_auth(username='user4', password='user4', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

        json_data = response.json()[0]
        self._checkJson(json_data)
        current_id = json_data['id_user_group']

        json_data = {
            'user_group': {
                'id_user_group': current_id,
                'user_group_name': 'Test2',
                'user_group_sites_access': [{
                    'id_site': 1,
                    'site_access_role': 'user'
                }],
                'user_group_projects_access': [
                    {
                        'id_project': 2,
                        'project_access_role': 'admin'
                    }
                ]
            }
        }
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update OK")
        json_reply = response.json()[0]
        self._checkJson(json_reply)
        self.assertEqual(json_reply['user_group_name'], 'Test2')
        self.assertEqual(len(json_reply['user_group_sites_access']), 1)
        self.assertEqual(json_reply['user_group_sites_access'][0]['id_site'], 1)
        self.assertEqual(json_reply['user_group_sites_access'][0]['site_access_role'], 'user')
        self.assertEqual(len(json_reply['user_group_projects_access']), 1)
        self.assertEqual(json_reply['user_group_projects_access'][0]['id_project'], 2)
        self.assertEqual(json_reply['user_group_projects_access'][0]['project_access_role'], 'admin')

        json_data['user_group']['user_group_sites_access'][0]['site_access_role'] = ''
        json_data['user_group']['user_group_projects_access'][0]['project_access_role'] = ''
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update removing roles OK")
        json_reply = response.json()[0]
        self._checkJson(json_reply)
        self.assertEqual(len(json_reply['user_group_sites_access']), 0)
        self.assertEqual(len(json_reply['user_group_projects_access']), 0)

        response = self._delete_with_http_auth(username='user4', password='user4', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_user_group'))
        self.assertTrue(json_data.__contains__('user_group_name'))

        if minimal:
            self.assertFalse(json_data.__contains__('user_group_sites_access'))
            self.assertFalse(json_data.__contains__('user_group_projects_access'))
