from tests.modules.FlaskModule.API.service.BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraUserUserGroup import TeraUserUserGroup
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraServiceRole import TeraServiceRole


class ServiceQueryUserGroupsTest(BaseServiceAPITest):
    test_endpoint = '/api/service/usergroups'

    def setUp(self):
        super().setUp()

        # Add access to user group to this service
        with self._flask_app.app_context():
            role = TeraServiceRole.get_service_roles(self.id_service)
            self.id_service_role = role[0].id_service_role

            access = TeraServiceAccess()
            access.id_user_group = 1
            access.id_service_role = self.id_service_role
            TeraServiceAccess.insert(access)
            self.id_service_access = access.id_service_access

    def tearDown(self):
        super().tearDown()
        with self._flask_app.app_context():
            TeraServiceAccess.delete(self.id_service_access)

    def test_get_endpoint_no_auth(self):
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

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_without_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token)
            self.assertEqual(200, response.status_code)
            access = TeraServiceAccess.query.join(TeraServiceRole).\
                filter(TeraServiceRole.id_service == self.id_service).\
                filter(TeraServiceAccess.id_user_group is not None).all()
            ugs_ids = set([sa.id_user_group for sa in access])
            target_count = len(ugs_ids)
            json_data = response.json
            self.assertEqual(target_count, len(json_data))
            for user_group in json_data:
                self._checkJson(user_group, minimal=True)

    def test_query_specific_user_group(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                         params={'id_user_group': 2})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                         params={'id_user_group': 1})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data[0], minimal=True)
            self.assertEqual(json_data[0]['id_user_group'], 1)

    def test_get_usergroups_for_forbidden_project(self):
        with self._flask_app.app_context():
            params = {'id_project': 2}
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(403, response.status_code)

    def test_get_usergroups_for_project(self):
        with self._flask_app.app_context():
            params = {'id_project': 1}
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(200, response.status_code)
            for json_data in response.json:
                self._checkJson(json_data)

    def test_get_usergroups_for_forbidden_site(self):
        with self._flask_app.app_context():
            params = {'id_site': 2}
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(403, response.status_code)

    def test_get_usergroups_for_site(self):
        with self._flask_app.app_context():
            params = {'id_site': 1}
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(200, response.status_code)
            for json_data in response.json:
                self._checkJson(json_data)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                'id_user_group': 0,
                'user_group_name': 'Testing123'
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing user group")

            json_data = {
                'user_group': {
                }
            }

            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing id_user_group")

            json_data['user_group']['id_user_group'] = 0
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing user group name")

            json_data['user_group']['user_group_name'] = 'Testing123'
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing service role for new user group")

            json_data['user_group']['user_group_services_access'] = [{'id_service': 1}]
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing role name or id_service_role")

            json_data['user_group']['user_group_services_access'] = [{'service_role_name': 'admin', 'id_service': 1}]
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 403, msg="Bad service")

            json_data['user_group']['user_group_services_access'] = [{'service_role_name': 'admin', 'id_project': 3}]
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 403, msg="Bad project")

            json_data['user_group']['user_group_services_access'] = [{'service_role_name': 'admin', 'id_site': 2}]
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 403, msg="Bad site")

            json_data['user_group']['user_group_services_access'] = [{'service_role_name': 'Bad role'}]
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 400, msg="Bad role name")

            json_data['user_group']['user_group_services_access'] = [{'service_role_name': 'admin'},
                                                                     {'service_role_name': 'user'}]
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post new")  # All OK!

            json_data = response.json
            self._checkJson(json_data)
            current_id = json_data['id_user_group']
            access = TeraServiceAccess.get_service_access_for_user_group(id_service=self.id_service,
                                                                         id_user_group=current_id)
            self.assertEqual(2, len(access))

            json_data = {
                'user_group': {
                    'id_user_group': current_id,
                    'user_group_name': 'New name'
                }
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post update OK")
            json_reply = response.json
            self._checkJson(json_reply, minimal=True)
            self.assertEqual(json_reply['user_group_name'], 'New name')  # No change since the same id as before
            access = TeraServiceAccess.get_service_access_for_user_group(id_service=self.id_service,
                                                                         id_user_group=current_id)
            self.assertEqual(2, len(access))

            # Try to change some access role
            json_data = {
                'user_group': {
                    'id_user_group': current_id,
                    'user_group_services_access': [{'service_role_name': 'admin'}]
                }
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post update OK")
            access = TeraServiceAccess.get_service_access_for_user_group(id_service=self.id_service,
                                                                         id_user_group=current_id)
            self.assertEqual(1, len(access))

            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': 2})
            self.assertEqual(response.status_code, 403, msg="Delete denied")

            # Associate user with that usergroup
            user3 = TeraUser.get_user_by_username('user3')
            uug = TeraUserUserGroup()
            uug.id_user = user3.id_user
            uug.id_user_group = current_id
            TeraUserUserGroup.insert(uug)

            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': current_id})
            self.assertEqual(response.status_code, 500, msg="Delete denied - user in that user group")

            TeraUserUserGroup.delete(uug.id_user_user_group)
            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'id': current_id})
            self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_user_group'))
        self.assertTrue(json_data.__contains__('user_group_name'))
