from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraServiceAccess import TeraServiceAccess


class UserQueryServiceAccessTest(BaseUserAPITest):
    test_endpoint = '/api/user/services/access'

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

    def test_query_for_service(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_service': 4})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 4})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_service'], 4)

    def test_query_for_user_group(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_user_group': 2})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user_group': 2})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_user_group'], 2)
                self.assertTrue(data_item.__contains__('user_group_name'))

    def test_query_for_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_user': 2})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 4})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            user = TeraUser.get_user_by_id(4)
            user_group_ids = [ug.id_user_group for ug in user.user_user_groups]
            target_count = TeraServiceAccess.query.filter(
                TeraServiceAccess.id_user_group.in_(user_group_ids)).count()
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_for_device(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_device': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_device': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_device'], 1)
                self.assertTrue(data_item.__contains__('device_name'))

    def test_query_for_participant_group(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_participant_group': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_participant_group': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_participant_group'], 1)
                self.assertTrue(data_item.__contains__('participant_group_name'))

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {
                'service_access': {
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service_access")

            json_data['service_access']['id_service_access'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing at least one id field")

            json_data['service_access']['id_user_group'] = 1
            json_data['service_access']['id_device'] = 1
            json_data['service_access']['id_participant_group'] = 1
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Cant combine ids")

            del json_data['service_access']['id_device']
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Cant combine ids")

            del json_data['service_access']['id_participant_group']
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service_role")

            json_data['service_access']['id_service_role'] = 5
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

            json_data = response.json[0]
            current_id = json_data['id_service_access']

            json_data = {
                'service_access': {
                    'id_service_access': current_id
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Deleted access")
            self.assertEqual(1, len(response.json))

            json_data = {
                'service_access': {
                    'id_service_access': 0,
                    'id_service_role': 5,
                    'id_participant_group': 1
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post new")  # All ok

            json_data = response.json[0]
            self.assertEqual(json_data['id_service_role'], 5)
            self.assertEqual(json_data['id_participant_group'], 1)

            current_id = json_data['id_service_access']

            json_data = {
                'service_access': {
                    'id_service_access': current_id,
                    'id_service_role': 6
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post update OK")
            json_data = response.json[0]
            self.assertEqual(json_data['id_service_role'], 6)

            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
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
