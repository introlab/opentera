from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest


class UserQueryStatsTest(BaseUserAPITest):
    test_endpoint = '/api/user/stats'

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
            self.assertEqual(405, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_http_auth(self.test_client)
            self.assertEqual(405, response.status_code)

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(400, response.status_code)

    def test_query_user_group_stats(self):
        with self._flask_app.app_context():
            params = {'id_user_group': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_user_stats(self):
        with self._flask_app.app_context():
            params = {'id_user': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_site_stats(self):
        with self._flask_app.app_context():
            params = {'id_site': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_project_stats(self):
        with self._flask_app.app_context():
            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_participant_group_stats(self):
        with self._flask_app.app_context():
            params = {'id_group': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_session_stats(self):
        with self._flask_app.app_context():
            params = {'id_session': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_participant_stats(self):
        with self._flask_app.app_context():
            params = {'id_participant': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)

    def test_query_device_stats(self):
        with self._flask_app.app_context():
            params = {'id_device': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(403, response.status_code)
