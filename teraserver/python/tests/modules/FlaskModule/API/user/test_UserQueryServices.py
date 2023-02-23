from BaseUserAPITest import BaseUserAPITest


class UserQueryServicesTest(BaseUserAPITest):
    test_endpoint = '/api/user/services'

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
            self.assertEqual(len(response.json), 5)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user')
            self.assertGreater(len(response.json), 0)

    def test_query_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                # Logger service should not be here since a system service!
                # self.assertNotEqual(data_item['id_service'], 2)
                # ... but not allowed when requesting as superadmin!

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 0)

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            # OpenTera service is a system service, and should not be returned here!
            self.assertEqual(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 4})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 1)

            service_uuid = None
            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_service'], 4)
                service_uuid = data_item['service_uuid']

            # Now try to query with service uuid
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'uuid': service_uuid})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_service'], 4)
                self.assertEqual(data_item['service_uuid'], service_uuid)

    def test_query_services_for_project_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 2)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_services_for_site_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 3)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_by_key_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'key': 'VideoRehabService'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['service_key'], 'VideoRehabService')

    def test_query_with_config_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'with_config': 1, 'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            json_data = response.json
            self.assertGreaterEqual(len(json_data), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {
                'service': {
                        "service_clientendpoint": "/",
                        "service_enabled": True,
                        "service_endpoint": "/test",
                        "service_hostname": "localhost",
                        "service_name": "Test",
                        "service_port": 0,
                        "service_config_schema": "{"
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing id_service")  # Missing id_service

            json_data['service']['id_service'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing service_key")

            json_data['service']['service_key'] = 'Test'
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            # json=json_data)
            # self.assertEqual(response.status_code, 400, msg="Invalid insert service_config_schema")

            del json_data['service']['service_config_schema']  # Will use default value
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post new")  # All ok now!

            json_data = response.json[0]
            self._checkJson(json_data)
            current_id = json_data['id_service']

            json_data = {
                'service': {
                    'id_service': current_id,
                    'service_enabled': False,
                    'service_system': False,
                    'service_name': 'Test2',
                    'service_key': 'service_key',
                    'service_config_schema': '{Test'
                }
            }
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            # json=json_data)
            # self.assertEqual(403, response.status_code, msg="Post update with service_system that shouldn't be here")

            # del json_data['service']['service_system']
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            # json=json_data)
            # self.assertEqual(response.status_code, 400, msg="Post update with invalid config schema")

            del json_data['service']['service_config_schema']
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post update OK")
            json_data = response.json[0]
            self._checkJson(json_data)
            self.assertEqual(json_data['service_enabled'], False)
            self.assertEqual(json_data['service_name'], 'Test2')

            # Check that default service roles (admin, user) were created
            self.assertTrue(json_data.__contains__('service_roles'))
            self.assertEqual(len(json_data['service_roles']), 2)
            self.assertEqual(json_data['service_roles'][0]['service_role_name'], 'admin')
            self.assertEqual(json_data['service_roles'][1]['service_role_name'], 'user')

            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(200, response.status_code, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('service_uuid'))
        self.assertTrue(json_data.__contains__('service_name'))
        self.assertTrue(json_data.__contains__('service_key'))
        self.assertTrue(json_data.__contains__('service_hostname'))
        self.assertTrue(json_data.__contains__('service_port'))
        self.assertTrue(json_data.__contains__('service_endpoint'))
        self.assertTrue(json_data.__contains__('service_clientendpoint'))
        self.assertTrue(json_data.__contains__('service_enabled'))
        self.assertTrue(json_data.__contains__('service_editable_config'))

        if not minimal:
            self.assertTrue(json_data.__contains__('service_roles'))
            self.assertTrue(json_data.__contains__('service_projects'))
            # self.assertTrue(json_data.__contains__('service_editable_config'))
        else:
            self.assertFalse(json_data.__contains__('service_roles'))
            self.assertFalse(json_data.__contains__('service_projects'))
            # self.assertFalse(json_data.__contains__('service_editable_config'))
