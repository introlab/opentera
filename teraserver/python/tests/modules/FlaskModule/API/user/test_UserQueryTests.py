from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest


class UserQueryTestsTest(BaseUserAPITest):
    test_endpoint = '/api/user/tests'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_no_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client)
            self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(self.test_client)
            self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_http_auth(self.test_client)
            self.assertEqual(401, response.status_code)

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(400, response.status_code)

    def test_query_bad_params_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_invalid': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', 
                                                     params=params)
            self.assertEqual(400, response.status_code)

    def test_query_device_tests_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_device': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', 
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_device_tests_no_access(self):
        with self._flask_app.app_context():
            params = {'id_device': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_session_tests_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_session': 2, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_session_tests_no_access(self):
        with self._flask_app.app_context():
            params = {'id_session': 2}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_participant_tests_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_participant': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_participant_tests_no_access(self):
        with self._flask_app.app_context():
            params = {'id_participant': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_user_tests_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_user': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_user_tests_no_access(self):
        with self._flask_app.app_context():
            params = {'id_user': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_test_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_test': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_test_no_access(self):
        with self._flask_app.app_context():
            params = {'id_test': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

    def test_post_as_admin(self):
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json={}, )
            self.assertEqual(501, response.status_code)

    def test_delete_as_admin(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': 44})
            self.assertEqual(403, response.status_code)

            # This will cause issues, since numbers won't match afterwards... Improve.
            # response = self._delete_with_user_http_auth(username='admin', password='admin', params={'id': 1},
            #                                             )
            # self.assertEqual(200, response.status_code)

    def test_query_session_tests_as_admin_token_only(self):
        with self._flask_app.app_context():
            params = {'id_session': 2, 'with_urls': True, 'with_only_token': True}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(3, len(response.json))
            for data_item in response.json:
                self.assertFalse(data_item.__contains__("test_name"))
                self.assertTrue(data_item.__contains__("test_uuid"))
                self.assertTrue(data_item.__contains__("access_token"))

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_test'))
        self.assertTrue(json_data.__contains__('id_session'))
        self.assertTrue(json_data.__contains__('id_device'))
        self.assertTrue(json_data.__contains__('id_participant'))
        self.assertTrue(json_data.__contains__('id_user'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('test_name'))
        self.assertTrue(json_data.__contains__('test_uuid'))
        self.assertTrue(json_data.__contains__('test_summary'))
        self.assertTrue(json_data.__contains__('test_status'))
        self.assertTrue(json_data.__contains__('test_datetime'))
        if not minimal:
            self.assertTrue(json_data.__contains__('test_answers_url'))
            self.assertTrue(json_data.__contains__('test_answers_web_url'))
            self.assertTrue(json_data.__contains__('access_token'))
