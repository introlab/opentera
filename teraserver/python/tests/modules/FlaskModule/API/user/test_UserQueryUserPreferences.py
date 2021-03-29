from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import datetime


class UserQueryUserPreferencesTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/users/preferences'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_auth(self):
        response = self._request_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_post_no_auth(self):
        response = self._post_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_query_no_params_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

    def test_query_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="id_user=1")
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

    def test_query_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user'], 1)

    def test_query_specific_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user'], 2)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user'], 2)
            self.assertEqual(data_item['user_preference_app_tag'], 'openteraplus')

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=1&"
                                                                                            "app_tag=openteraplus")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_user'], 1)
            self.assertEqual(data_item['user_preference_app_tag'], 'openteraplus')

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'user_preference': {
                "id_user": 2,
                "user_preference_preference": "{err"
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing app_tag")  # Missing app+tag

        json_data['user_preference']['user_preference_app_tag'] = 'testapp'
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="JSON format error")

        json_data['user_preference']['user_preference_preference'] = '{"TestParam": 1234}'
        response = self._post_with_http_auth(username='user4', password='user4', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

        json_data = response.json()
        self._checkJson(json_data)
        self.assertEqual(json_data['user_preference_preference'], '{"TestParam": 1234}')

        json_data = {
            'user_preference': {
                "id_user": 2,
                'user_preference_app_tag': 'testapp',
                'user_preference_preference': '{"TestParam": 4567}'
            }
        }
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update")

        json_data = response.json()
        self._checkJson(json_data)
        self.assertEqual(json_data['user_preference_preference'], '{"TestParam": 4567}')

        json_data = {
            'user_preference': {
                "id_user": 2,
                'user_preference_app_tag': 'testapp'
            }
        }
        # Delete prefs
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post delete prefs")

        # Check everything was deleted
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_user=2&"
                                                                                            "app_tag=testapp")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        # Try to update self preferences
        json_data = {
            'user_preference': {
                'user_preference_app_tag': 'testapp',
                'user_preference_preference': '{"TestParam": "TEST"}'
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post self new")

        # Delete prefs
        json_data['user_preference']['user_preference_preference'] = ''
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post delete self prefs")

        # Check everything was deleted
        response = self._request_with_http_auth(username='admin', password='admin', payload="app_tag=testapp")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_user'))
        self.assertTrue(json_data.__contains__('id_user_preference'))
        self.assertTrue(json_data.__contains__('user_preference_app_tag'))
        self.assertTrue(json_data.__contains__('user_preference_preference'))

