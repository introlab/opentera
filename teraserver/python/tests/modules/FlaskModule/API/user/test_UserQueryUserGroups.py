from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUserGroup import TeraUserGroup
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraUserUserGroup import TeraUserUserGroup


class UserQueryUserGroupsTest(BaseUserAPITest):
    test_endpoint = '/api/user/usergroups'

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

    def test_without_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(200, response.status_code)
            target_count = TeraUserGroup.get_count()
            json_data = response.json
            self.assertEqual(len(json_data), target_count)
            for user_group in json_data:
                self._checkJson(user_group)

    def test_without_params_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3')
            self.assertEqual(200, response.status_code)
            json_data = response.json
            for user_group in json_data:
                self._checkJson(user_group)

    def test_query_specific_user_group_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 1})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data[0], minimal=False)
            self.assertEqual(json_data[0]['id_user_group'], 1)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 1, 'list': 1})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data[0], minimal=True)
            self.assertEqual(json_data[0]['id_user_group'], 1)

    def test_query_specific_user_group_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_user_group': 1})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'id_user_group': 1})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data[0], minimal=False)
            self.assertEqual(json_data[0]['id_user_group'], 1)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'id_user_group': 1, 'list': 1})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data[0], minimal=True)
            self.assertEqual(json_data[0]['id_user_group'], 1)

    def test_query_for_user_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 1})
            self.assertEqual(200, response.status_code, msg='Super admin = no user groups')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 3})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            target_count = len(TeraUser.get_user_by_id(3).user_user_groups)
            self.assertEqual(len(json_data), target_count)
            for ug_data in json_data:
                self._checkJson(ug_data, minimal=False)

    def test_query_for_user_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_user': 3})
            self.assertEqual(200, response.status_code, msg='No access to that user')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                     params={'id_user': 2})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            target_count = len(TeraUser.get_user_by_id(2).user_user_groups)
            self.assertEqual(len(json_data), target_count)
            for ug_data in json_data:
                self._checkJson(ug_data, minimal=False)

    def test_query_for_site_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            services_access = (TeraServiceAccess.get_service_access_for_site(
                id_service=TeraService.get_openteraserver_service().id_service, id_site=1))
            ug_ids = []
            for sa in services_access:
                if sa.service_access_user_group:
                    id_ug = sa.service_access_user_group.id_user_group
                    if id_ug not in ug_ids:
                        ug_ids.append(id_ug)

            # projects = TeraProject.query_data({'id_site': 1})
            projects = TeraProject.query_with_filters({'id_site': 1})
            for project in projects:
                services_access = (TeraServiceAccess.get_service_access_for_project(
                    id_service=TeraService.get_openteraserver_service().id_service, id_project=project.id_project))
                for sa in services_access:
                    if sa.service_access_user_group:
                        id_ug = sa.service_access_user_group.id_user_group
                        if id_ug not in ug_ids:
                            ug_ids.append(id_ug)

            self.assertEqual(len(json_data), len(ug_ids))
            for ug_data in json_data:
                self._checkJson(ug_data, minimal=False)

    def test_query_for_site_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code, msg='No access')
            json_data = response.json
            self.assertEqual(len(json_data), 0)
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            services_access = (TeraServiceAccess.get_service_access_for_site(
                id_service=TeraService.get_openteraserver_service().id_service, id_site=1))
            ug_ids = []
            for sa in services_access:
                if sa.service_access_user_group:
                    id_ug = sa.service_access_user_group.id_user_group
                    if id_ug not in ug_ids:
                        ug_ids.append(id_ug)

            # projects = TeraProject.query_data({'id_site': 1})
            projects = TeraProject.query_with_filters({'id_site': 1})
            for project in projects:
                services_access = (TeraServiceAccess.get_service_access_for_project(
                    id_service=TeraService.get_openteraserver_service().id_service, id_project=project.id_project))
                for sa in services_access:
                    if sa.service_access_user_group:
                        id_ug = sa.service_access_user_group.id_user_group
                        if id_ug not in ug_ids:
                            ug_ids.append(id_ug)

            self.assertEqual(len(json_data), len(ug_ids))
            for ug_data in json_data:
                self._checkJson(ug_data, minimal=False)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                'id_user_group': 0,
                'user_group_name': 'Testing123'
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing user group")

            json_data = {
                'user_group': {
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing id_user_group")

            json_data['user_group']['id_user_group'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing user group name")

            json_data['user_group']['user_group_name'] = 'Testing123'
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(response.status_code, 403, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

            json_data = response.json[0]
            self._checkJson(json_data, minimal=True)
            current_id = json_data['id_user_group']

            json_data = {
                'user_group': {
                    'id_user_group': current_id,
                    'user_group_name': 'New name'
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post update OK")
            json_reply = response.json[0]
            self._checkJson(json_reply, minimal=True)
            self.assertEqual(json_reply['user_group_name'], 'New name')  # No change since the same id as before

            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params={'id': current_id})
            self.assertEqual(response.status_code, 403, msg="Delete denied")

            # Associate user with that usergroup
            user3 = TeraUser.get_user_by_username('user3')
            uug = TeraUserUserGroup()
            uug.id_user = user3.id_user
            uug.id_user_group = current_id
            TeraUserUserGroup.insert(uug)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(response.status_code, 500, msg="Delete denied - user in that user group")

            TeraUserUserGroup.delete(uug.id_user_user_group)
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_user_group'))
        self.assertTrue(json_data.__contains__('user_group_name'))

        if minimal:
            self.assertFalse(json_data.__contains__('user_group_projects_access'))
            self.assertFalse(json_data.__contains__('user_group_sites_access'))
        else:
            self.assertTrue(json_data.__contains__('user_group_projects_access'))
            self.assertTrue(json_data.__contains__('user_group_sites_access'))
