from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from modules.FlaskModule.FlaskModule import flask_app


class UserQueryTestsTest(BaseUserAPITest):
    test_endpoint = '/api/user/tests'

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
            self.assertEqual(response.status_code, 400)

    def test_query_bad_params_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_invalid': 1}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 400)

    def test_query_device_tests_as_admin(self):
        with self._flask_app.app_context():
            payload = {'id_device': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=payload,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)

            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_device_tests_no_access(self):
        with self._flask_app.app_context():
            payload = {'id_device': 1}
            response = self._get_with_user_http_auth(username='user4', password='user4', params=payload,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 403)

    def test_query_session_tests_as_admin(self):
        with self._flask_app.app_context():
            payload = {'id_session': 2, 'with_urls': True}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=payload,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)

            json_data = response.json
            self.assertTrue(len(json_data), 3)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_session_tests_no_access(self):
        with self._flask_app.app_context():
            payload = {'id_session': 2}
            response = self._get_with_user_http_auth(username='user4', password='user4', params=payload,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 403)

    def test_query_participant_tests_as_admin(self):
        with self._flask_app.app_context():
            payload = {'id_participant': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=payload,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)

            json_data = response.json
            self.assertTrue(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_participant_tests_no_access(self):
        with self._flask_app.app_context():
            payload = {'id_participant': 1}
            response = self._get_with_user_http_auth(username='user4', password='user4', params=payload,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 403)

    def test_query_user_tests_as_admin(self):
        with self._flask_app.app_context():
            payload = {'id_user': 2}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=payload,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)

            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_user_tests_no_access(self):
        with self._flask_app.app_context():
            payload = {'id_user': 1}
            response = self._get_with_user_http_auth(username='user4', password='user4', params=payload,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 403)

    def test_query_test_as_admin(self):
        with self._flask_app.app_context():
            payload = {'id_test': 1, 'with_urls': True}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=payload,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)

            json_data = response.json
            self.assertTrue(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_test_no_access(self):
        with self._flask_app.app_context():
            payload = {'id_test': 1}
            response = self._get_with_user_http_auth(username='user4', password='user4', params=payload,
                                                     client=self.test_client)
            json_data = response.json
            self.assertEqual(len(json_data), 0)
            self.assertEqual(response.status_code, 200)

    def test_post_as_admin(self):
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(username='admin', password='admin',
                                                      json={}, client=self.test_client)
            self.assertEqual(response.status_code, 501)

    def test_delete_as_admin(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_http_auth(username='admin', password='admin', params={'id': 44},
                                                        client=self.test_client)
            self.assertEqual(response.status_code, 403)

            # This will cause issues, since numbers won't match afterwards... Improve.
            # response = self._delete_with_user_http_auth(username='admin', password='admin', params={'id': 1},
            #                                             client=self.test_client)
            # self.assertEqual(response.status_code, 200)

    def test_query_session_tests_as_admin_token_only(self):
        with self._flask_app.app_context():
            payload = {'id_session': 2, 'with_urls': True, 'with_only_token': True}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=payload,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)

            json_data = response.json
            self.assertEqual(len(json_data), 3)
            for data_item in json_data:
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
