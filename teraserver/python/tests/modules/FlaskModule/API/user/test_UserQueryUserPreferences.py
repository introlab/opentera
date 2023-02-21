from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser


class UserQueryUserPreferencesTest(BaseUserAPITest):
    test_endpoint = '/api/user/users/preferences'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_no_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(client=self.test_client)
            self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(client=self.test_client)
            self.assertEqual(401, response.status_code)

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))
            for pref in response.json:
                self._checkJson(pref)

    def test_query_as_user_with_non_accessible_user(self):
        with self._flask_app.app_context():
            params = {'id_user': 1}  # admin
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(403, response.status_code)

    def test_query_as_user_with_self_user(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('user')
            params = {'id_user': user.id_user}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)

            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            for pref in response.json:
                self._checkJson(pref)

    def test_query_all_as_admin(self):
        with self._flask_app.app_context():
            for user in TeraUser.query.all():
                params = {'id_user': user.id_user}
                response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                         params=params)
                self.assertEqual(200, response.status_code)
                self.assertTrue(response.is_json)

                for data_item in response.json:
                    self._checkJson(json_data=data_item)

    def test_query_all_with_specific_tag_as_admin(self):
        with self._flask_app.app_context():
            for user in TeraUser.query.all():
                params = {'id_user': user.id_user,
                          'app_tag': 'openteraplus'}
                response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                         params=params)
                self.assertEqual(200, response.status_code)
                self.assertTrue(response.is_json)

                for data_item in response.json:
                    self._checkJson(json_data=data_item)
                    self.assertEqual('openteraplus', data_item['user_preference_app_tag'])

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {
                'user_preference': {
                    "id_user": 2,
                    "user_preference_preference": "{err"
                }
            }

            response = self._post_with_user_http_auth(self.test_client,
                                                      username='admin', password='admin', json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing app_tag")  # Missing app+tag

            json_data['user_preference']['user_preference_app_tag'] = 'testapp'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="JSON format error")

            json_data['user_preference']['user_preference_preference'] = '{"TestParam": 1234}'
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Post denied for user")  # Forbidden

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post new")  # All ok now!

            self._checkJson(response.json)
            self.assertEqual(response.json['user_preference_preference'], '{"TestParam": 1234}')

            json_data = {
                'user_preference': {
                    "id_user": 2,
                    'user_preference_app_tag': 'testapp',
                    'user_preference_preference': '{"TestParam": 4567}'
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post update")
            self._checkJson(response.json)
            self.assertEqual(response.json['user_preference_preference'], '{"TestParam": 4567}')

            json_data = {
                'user_preference': {
                    "id_user": 2,
                    'user_preference_app_tag': 'testapp'
                }
            }
            # Delete prefs
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post delete prefs")

            # Check everything was deleted
            params = {'id_user': 2, 'app_tag': 'testapp'}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 0)

            # Try to update self preferences
            json_data = {
                'user_preference': {
                    'user_preference_app_tag': 'testapp',
                    'user_preference_preference': '{"TestParam": "TEST"}'
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post self new")

            # Delete prefs
            json_data['user_preference']['user_preference_preference'] = ''
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=json_data)
            self.assertEqual(200, response.status_code, msg="Post delete self prefs")

            # Check everything was deleted
            params = {'app_tag': 'testapp'}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code, 200)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 0)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_user'))
        self.assertTrue(json_data.__contains__('id_user_preference'))
        self.assertTrue(json_data.__contains__('user_preference_app_tag'))
        self.assertTrue(json_data.__contains__('user_preference_preference'))
