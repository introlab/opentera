from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraService import TeraService


class UserQueryServiceConfigsTest(BaseUserAPITest):
    test_endpoint = '/api/user/services/configs'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_no_auth(self):
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
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_user'], 1)

    def test_query_combined_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 1, 'id_user': 1, 'id_participant': 1})
            self.assertEqual(400, response.status_code)
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 1, 'id_user': 1, 'id_device': 1})
            self.assertEqual(400, response.status_code)
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 1, 'id_participant': 1, 'id_device': 1})
            self.assertEqual(400, response.status_code)

    def test_query_for_service_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_service'], 1)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'service_key': 'VideoRehabService'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreaterEqual(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['service_config_name'], 'Télé-réadaptation vidéo')

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 1, 'with_schema': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 1, 'with_empty': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                if data_item['id_service'] == 6:
                    self.assertEqual(data_item['id_service_config'], None)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 1, 'with_empty': 1, 'with_schema': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                if data_item['id_service'] == 6:
                    self.assertEqual(data_item['id_service_config'], None)

    def test_query_for_user_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_user': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_user'], 1)

    def test_query_for_device_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_device': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_device'], 1)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_device': 1, 'with_empty': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                if data_item['id_service'] == 1:
                    self.assertEqual(data_item['id_service_config'], None)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_device': 1, 'with_empty': 1, 'with_schema': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                if data_item['id_service'] == 1:
                    self.assertEqual(data_item['id_service_config'], None)

    def test_query_for_participant_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_participant': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_participant'], 1)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_participant': 1, 'with_empty': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_participant': 1, 'with_empty': 1, 'with_schema': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

            # Check specific ids VS global
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_participant': 1, 'id_specific': 'pc-001'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_participant'], 1)
                self.assertEqual(data_item['service_config_specific_id'], 'pc-001')

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_participant': 1, 'id_specific': 'pc-xxx'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_participant'], 1)
                self.assertEqual(data_item['service_config_specific_id'], None)

    def test_query_specific_as_admin(self):
        with self._flask_app.app_context():
            service : TeraService = TeraService.get_service_by_key('OpenTeraServer')
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': service.id_service, 'id_user': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))
            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_user'], 1)
                self.assertEqual(data_item['id_service'], service.id_service)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': service.id_service, 'id_user': 2})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            service: TeraService = TeraService.get_service_by_key('VideoRehabService')
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': service.id_service, 'id_participant': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))
            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_participant'], 1)
                self.assertEqual(data_item['id_service'], service.id_service)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': service.id_service, 'id_device': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))
            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_device'], 1)
                self.assertEqual(data_item['id_service'], service.id_service)

    def test_post_and_delete(self):
        with self._flask_app.app_context():

            json_data = {
                'service_config': {
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service_config")  # Missing id_service_config

            json_data['service_config']['id_service_config'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service")

            json_data['service_config']['id_service'] = 3
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing at least one id")

            json_data['service_config']['id_user'] = 1
            response = self._post_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post new")  # All ok now!

            json_data = response.json[0]
            self._checkJson(json_data)
            current_id = json_data['id_service_config']

            json_data = {
                'service_config': {
                    'id_service_config': current_id,
                    'service_config_config': '{"Test": "123"}'
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post update OK")

            json_data['service_config']['service_config_config'] = '{"Test": "456"}'
            json_data['service_config']['id_specific'] = 'Test Spec'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post specific config OK")
            json_data = response.json[0]
            self._checkJson(json_data)

            # Check config
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 3, 'id_user': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))
            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['service_config_config']['Test'], '123')
                self.assertEqual(data_item['service_config_specific_id'], None)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 3, 'id_user': 1, 'id_specific': 'Test Spec'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))
            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['service_config_config']['Test'], '456')
                self.assertEqual(data_item['service_config_specific_id'], 'Test Spec')

            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(200, response.status_code, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_service_config'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('service_config_config'))
        self.assertTrue(json_data.__contains__('service_config_last_update_time'))
        self.assertTrue(json_data.__contains__('service_config_name'))
