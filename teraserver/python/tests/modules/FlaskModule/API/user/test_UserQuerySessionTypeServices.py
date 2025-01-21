from opentera.db.models import TeraSessionTypeServices
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

    def test_post_session_type(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing everything")  # Missing

            json_data = {'session_type': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_session_type")

            json_data = {'session_type': {'id_session_type': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing services")

            json_data = {'session_type': {'id_session_type': 1, 'services': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only project/site admins can change things here")

            json_data = {'session_type': {'id_session_type': 5, 'services': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove from all services OK")

            params = {'id_session_type': 5}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            json_data = {'session_type': {'id_session_type': 5, 'services': [{'id_service': 1},
                                                                             {'id_service': 2},
                                                                             {'id_service': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all services OK")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(3, len(response.json))  # Everything was added

            json_data = {'session_type': {'id_session_type': 5, 'services': [{'id_service': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove one service")
            self.assertIsNotNone(TeraSessionTypeServices.get_session_type_service_for_session_type_service(
                session_type_id=5, service_id=1))
            self.assertIsNone(TeraSessionTypeServices.get_session_type_service_for_session_type_service(
                session_type_id=5, service_id=2))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

    def test_post_service(self):
        with self._flask_app.app_context():
            service = TeraService.get_service_by_key('EmailService')
            json_data = {}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing everything")  # Missing

            json_data = {'service': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service")

            json_data = {'service': {'id_service': service.id_service}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing sessiontypes")

            json_data = {'service': {'id_service': service.id_service, 'sessiontypes': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only project/site admins can change things here")

            json_data = {'service': {'id_service': service.id_service, 'sessiontypes': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove all sessiontypes OK")


            sts = TeraSessionTypeServices.get_sessions_types_for_service(service.id_service)
            self.assertEqual(0, len(sts))  # Everything was deleted!

            json_data = {'service': {'id_service': service.id_service, 'sessiontypes': [{'id_session_type': 5},
                                                                             {'id_session_type': 4}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all session types OK")

            sts = TeraSessionTypeServices.get_sessions_types_for_service(service.id_service)
            self.assertEqual(2, len(sts))  # Everything was added

            json_data = {'service': {'id_service': service.id_service, 'sessiontypes': [{'id_session_type': 4}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove one service")
            self.assertIsNotNone(TeraSessionTypeServices.get_session_type_service_for_session_type_service(
                session_type_id=4, service_id=service.id_service))
            self.assertIsNone(TeraSessionTypeServices.get_session_type_service_for_session_type_service(
                session_type_id=5, service_id=service.id_service))

            sts = TeraSessionTypeServices.get_sessions_types_for_service(service.id_service)
            self.assertEqual(1, len(sts))

            # Back to normal
            for st in sts:
                TeraSessionTypeServices.delete(st.id_session_type_service)

    def test_post_session_type_service_and_delete(self):
        with self._flask_app.app_context():
            service = TeraService.get_service_by_key('EmailService')
            json_data = {'session_type_service': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'session_type_service': {'id_service': service.id_service}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'session_type_service': {'id_service': service.id_service, 'id_session_type': 4}}
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only site admins can change things here")

            json_data = {'session_type_service': {'id_service': service.id_service, 'id_session_type': 4}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add new association OK")

            sts = TeraSessionTypeServices.get_sessions_types_for_service(service.id_service)

            current_id = None
            for st in sts:
                if st.id_session_type == 4:
                    current_id = st.id_session_type_service
            self.assertFalse(current_id is None)

            response = self._delete_with_user_http_auth(self.test_client, username='user', password='user',
                                                        params={'id': current_id})
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params={'id': current_id})
            self.assertEqual(200, response.status_code, msg="Delete OK")

            sts = TeraSessionTypeServices.get_session_type_service_by_id(current_id)
            self.assertIsNone(sts)

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