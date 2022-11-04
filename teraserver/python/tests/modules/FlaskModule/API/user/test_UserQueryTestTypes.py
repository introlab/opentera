from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest


class UserQueryTestTypesTest(BaseUserAPITest):
    test_endpoint = '/api/user/testtypes'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_no_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(client=self.test_client)
            self.assertEqual(response.status_code, 401)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(client=self.test_client)
            self.assertEqual(response.status_code, 401)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_http_auth(client=self.test_client)
            self.assertEqual(response.status_code, 401)

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='admin', password='admin', client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 3)

            for data_item in json_data:
                self._checkJson(data_item)

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='admin', password='admin', params="list=1",
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 3)

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='admin', password='admin', params="id_test_type=1",
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_specific_project_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='admin', password='admin', params="id_project=2",
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(username='admin', password='admin', params="id_project=1&list=1",
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_site_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='admin', password='admin', params="id_site=2",
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

            response = self._get_with_user_http_auth(username='admin', password='admin', params="id_site=1&list=1",
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_site_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='user', password='user', params="id_site=2",
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 403)

            response = self._get_with_user_http_auth(username='user', password='user', params="id_site=1",
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {
                'test_type': {
                    'id_service': None,
                    'test_type_name': 'Test'
                }
            }

            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing id_test_type")

            json_data['test_type']['id_test_type'] = 0
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Missing id_service")

            json_data['test_type']['id_service'] = 3
            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing test_type_projects for siteadmin")

            json_data['test_type']['test_type_sites'] = [{'id_site': 1}]
            json_data['test_type']['test_type_projects'] = [{'id_project': 1}, {'id_project': 3}]
            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="No access to project!")

            json_data['test_type']['test_type_sites'] = [{'id_site': 2}]
            json_data['test_type']['test_type_projects'] = [{'id_project': 1}, {'id_project': 2}]
            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="No access to site")

            json_data['test_type']['test_type_sites'] = [{'id_site': 1}]
            response = self._post_with_user_http_auth(username='user4', password='user4', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Post OK")

            json_data = response.json[0]
            self._checkJson(json_data)
            current_id = json_data['id_test_type']

            json_data = {
                'test_type': {
                    'id_test_type': current_id,
                    'test_type_name': 'Test 2',
                    'test_type_has_json_format': True
                }
            }

            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Post update")
            reply_data = response.json[0]
            self._checkJson(reply_data)
            self.assertEqual(reply_data['test_type_name'], 'Test 2')
            self.assertEqual(reply_data['test_type_has_json_format'], True)

            json_data['test_type']['test_type_projects'] = [{'id_project': 1}]
            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Changed projects")

            # Check that the untouched project is still there
            response = self._get_with_user_http_auth(username='admin', password='admin',
                                                     params="id_test_type=" + str(current_id),
                                                     endpoint='/api/user/testtypes/projects',
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            reply_data = response.json
            self.assertEqual(len(reply_data), 1)

            response = self._delete_with_user_http_auth(username='user4', password='user4', params="id="+str(current_id),
                                                        client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Delete denied")

            response = self._delete_with_user_http_auth(username='siteadmin', password='siteadmin',
                                                        params="id="+str(current_id), client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Delete OK")

            # Remove created project-service association
            params = {'id_project': 3}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     endpoint='/api/user/services/projects', client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            id_service_project = json_data[0]['id_service_project']

            response = self._delete_with_user_http_auth(username='admin', password='admin',
                                                        params="id="+str(id_service_project),
                                                        endpoint='/api/user/services/projects', client=self.test_client)
            self.assertEqual(response.status_code, 200, msg='Back to default state!')

    def test_query_with_urls(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='admin', password='admin', client=self.test_client,
                                                     params={'with_urls': True})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 3)

            for data_item in json_data:
                self._checkJson(data_item)
                self.assertTrue(data_item.__contains__('test_type_json_url'))
                self.assertTrue(data_item.__contains__('test_type_web_url'))
                self.assertTrue(data_item.__contains__('test_type_web_editor_url'))
                self.assertTrue(data_item.__contains__('access_token'))

    def test_query_access_token_only(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='admin', password='admin', client=self.test_client,
                                                     params={'with_only_token': True})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 3)

            for data_item in json_data:
                self.assertEqual(len(data_item), 2)
                self.assertTrue(data_item.__contains__('test_type_uuid'))
                self.assertTrue(data_item.__contains__('access_token'))

    def test_query_test_type_by_key(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='admin', password='admin', client=self.test_client,
                                                     params={'test_type_key': 'PRE'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(data_item)
                self.assertEqual(data_item['test_type_key'], 'PRE')

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_test_type'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('test_type_uuid'))
        self.assertTrue(json_data.__contains__('test_type_name'))
        self.assertTrue(json_data.__contains__('test_type_key'))
        self.assertTrue(json_data.__contains__('test_type_has_json_format'))
        self.assertTrue(json_data.__contains__('test_type_has_web_format'))
        self.assertTrue(json_data.__contains__('test_type_has_web_editor'))
        if not minimal:
            self.assertTrue(json_data.__contains__('test_type_description'))
            self.assertTrue(json_data.__contains__('test_type_service_key'))
            self.assertTrue(json_data.__contains__('test_type_service_uuid'))
