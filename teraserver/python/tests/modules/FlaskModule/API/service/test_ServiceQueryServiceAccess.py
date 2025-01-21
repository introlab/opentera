from tests.modules.FlaskModule.API.service.BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraServiceRole import TeraServiceRole


class ServiceQueryAccessTest(BaseServiceAPITest):
    test_endpoint = '/api/service/serviceaccess'

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

    def test_get_endpoint_with_token_auth_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.delete(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_query_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token)
            self.assertEqual(400, response.status_code)

    def test_query_for_user_group(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                         params={'id_user_group': 2})
            self.assertEqual(200, response.status_code, msg='No access to user group')
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_service_token_auth(self.test_client, token=self.service_token,
                                                         params={'id_user_group': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_user_group'], 1)
                self.assertTrue(data_item.__contains__('user_group_name'))

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {
                'service_access': {
                }
            }

            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service_access")

            json_data['service_access']['id_service_access'] = 0
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing at least one id field")

            json_data['service_access']['id_user_group'] = 1
            json_data['service_access']['id_device'] = 1
            json_data['service_access']['id_participant_group'] = 1
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Cant combine ids")

            del json_data['service_access']['id_device']
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Cant combine ids")

            del json_data['service_access']['id_participant_group']
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service_role")

            json_data['service_access']['id_service_role'] = 1
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="Not accessible service role")

            json_data['service_access']['id_service_role'] = self.id_service_role
            json_data['service_access']['id_user_group'] = 2
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="Not accessible user group")

            json_data['service_access']['id_user_group'] = 1
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Post new OK")

            json_data = response.json[0]
            current_id = json_data['id_service_access']

            json_data = {
                'service_access': {
                    'id_service_access': current_id,
                    'id_service_role': self.id_service_role,
                    'id_participant_group': 2
                }
            }
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 403, msg="No access to group")

            json_data['service_access']['id_participant_group'] = 1
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(response.status_code, 200, msg="Update OK")

            params = {'id': 1}
            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            params = {'id': current_id}
            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token, params=params)
            self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertTrue(json_data.__contains__('id_service_access'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('id_service_role'))
        self.assertTrue(json_data.__contains__('service_role_name'))
        if not minimal:
            self.assertTrue(json_data.__contains__('service_name'))
            self.assertTrue(json_data.__contains__('service_key'))
            self.assertTrue(json_data.__contains__('id_service'))
            self.assertTrue(json_data.__contains__('service_access_role_name'))
        else:
            self.assertFalse(json_data.__contains__('service_name'))
            self.assertFalse(json_data.__contains__('service_key'))
            self.assertFalse(json_data.__contains__('id_service'))
            self.assertFalse(json_data.__contains__('service_access_role_name'))
