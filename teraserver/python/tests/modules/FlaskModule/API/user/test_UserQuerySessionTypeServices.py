from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraUser import TeraUser
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class UserQuerySessionTypeServicesTest(BaseUserAPITest):
    test_endpoint = '/api/user/sessiontypes/services'

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

    def test_query_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user')
            self.assertEqual(400, response.status_code)

    def test_query_forbidden_session_type(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 1}
            response = self._get_with_user_http_auth(self.test_client, params=params,
                                                     username='user4', password='user4')
            self.assertEqual(200, response.status_code)
            self.assertTrue(len(response.json) == 0)

    def test_query_session_type(self):
        with self._flask_app.app_context():
            session_types = TeraSessionType.query.all()
            for session_type in session_types:
                params = {'id_session_type': session_type.id_session_type}
                response = self._get_with_user_http_auth(self.test_client, params=params,
                                                         username='admin', password='admin')
                self.assertEqual(200, response.status_code)
                self.assertTrue(len(response.json) == len(session_type.session_type_secondary_services))
                if len(response.json) > 0:
                    for data in response.json:
                        self._validate_json(data)

    def test_query_session_type_with_services(self):
        with self._flask_app.app_context():
            session_types = TeraSessionType.query.all()
            services = TeraService.query.all()
            user: TeraUser = TeraUser.get_user_by_username('user')
            access = DBManagerTeraUserAccess(user)
            limited_services = access.get_accessible_services()
            for session_type in session_types:
                params = {'id_session_type': session_type.id_session_type, 'with_services': 1}
                response = self._get_with_user_http_auth(self.test_client, params=params,
                                                         username='admin', password='admin')
                self.assertEqual(200, response.status_code)
                self.assertTrue(len(response.json) == len(services))
                response = self._get_with_user_http_auth(self.test_client, params=params,
                                                         username='user', password='user')
                self.assertEqual(200, response.status_code)
                self.assertTrue(len(response.json) == len(limited_services))

    def test_query_session_type_list(self):
        with self._flask_app.app_context():
            session_types = TeraSessionType.query.all()
            for session_type in session_types:
                params = {'id_session_type': session_type.id_session_type, 'list': 1}
                response = self._get_with_user_http_auth(self.test_client, params=params,
                                                         username='admin', password='admin')
                self.assertEqual(200, response.status_code)
                self.assertTrue(len(response.json) == len(session_type.session_type_secondary_services))
                if len(response.json) > 0:
                    for data in response.json:
                        self._validate_json(data, minimal=True)

    def _validate_json(self, json, minimal=False):
        self.assertTrue('id_session_type' in json)
        self.assertTrue('id_session_type_service' in json)
        self.assertTrue('id_service' in json)
        if minimal:
            self.assertFalse('session_type_name' in json)
            self.assertFalse('service_name' in json)
        else:
            self.assertTrue('session_type_name' in json)
            self.assertTrue('service_name' in json)