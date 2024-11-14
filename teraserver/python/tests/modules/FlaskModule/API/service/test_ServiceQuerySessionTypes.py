from typing import List
from tests.modules.FlaskModule.API.service.BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraParticipant import TeraParticipant


class ServiceQuerySessionTypesTest(BaseServiceAPITest):
    """
    Test Session Types for service API. We are testing with requests with a service token
    related to the VideoRehabService as implemented in BaseServiceAPITest.
    """
    test_endpoint = '/api/service/sessiontypes'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)

            session_types: List[TeraSessionType] = TeraSessionType.query.all()
            service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
            from modules.DatabaseModule.DBManager import DBManager
            service_access = DBManager.serviceAccess(service)
            accessible_types = service_access.get_accessible_sessions_types()
            self.assertEqual(len(accessible_types), len(response.json))
            self.assertTrue(len(accessible_types) <= len(session_types))
            for session_type in accessible_types:
                json_value = session_type.to_json()
                self.assertTrue(json_value in response.json)

    def test_get_for_site(self):
        with self._flask_app.app_context():
            params = {'id_site': 2}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg='No access to site')
            self.assertEqual(0, len(response.json))

            params = {'id_site': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg='Get OK')

            target_count = len(TeraSessionTypeSite.get_sessions_types_for_site(1))
            self.assertEqual(target_count, len(response.json))

    def test_get_for_project(self):
        with self._flask_app.app_context():
            params = {'id_project': 2}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg='No access to project')
            self.assertEqual(0, len(response.json))

            params = {'id_project': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg='Get OK')

            target_count = len(TeraSessionTypeProject.get_sessions_types_for_project(1))
            self.assertEqual(target_count, len(response.json))

    def test_get_for_participant(self):
        with self._flask_app.app_context():
            params = {'id_participant': 5}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg='No access to participant')
            self.assertEqual(0, len(response.json))

            params = {'id_participant': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg='Get OK')

            participant = TeraParticipant.get_participant_by_id(1)
            target_count = len(TeraSessionTypeProject.get_sessions_types_for_project(participant.id_project))
            self.assertEqual(target_count, len(response.json))

    def test_get_specific(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 4}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg='No access to session type')
            self.assertEqual(0, len(response.json))

            params = {'id_session_type': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg='Get OK')
            self.assertEqual(1, len(response.json))

    def test_post_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_with_token_auth_no_json(self):
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=None, params=None, endpoint=self.test_endpoint)
            self.assertEqual(415, response.status_code)

    def test_post_endpoint_with_token_auth_invalid_schema(self):
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json={}, params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_post_endpoint_with_invalid_schema_without_session_type(self):
        with self._flask_app.app_context():

            json_data = {'service_session_type': {}} # Missing session_type
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_post_endpoint_with_invalid_schema_without_session_type_id_session_type(self):
        with self._flask_app.app_context():

            json_data = {'service_session_type': {'session_type': {}}} # Missing id_session_type
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_post_endpoint_with_invalid_schema_with_invalid_keys(self):
        with self._flask_app.app_context():

            json_data = {'service_session_type': {'session_type': {'id_session_type': 0,
                                                                   'invalid_key': 'invalid'}}}
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_post_endpoint_with_valid_schema_create_session_type_missing_fields(self):
        with self._flask_app.app_context():
            # session_type = TeraSessionType.get_session_type_by_id(1)
            json_data = {'service_session_type': {'session_type': {'id_session_type': 0}}}
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)


    def test_post_endpoint_with_valid_schema_create_session_type_with_inaccessible_sites(self):
        with self._flask_app.app_context():

            json_data = {'service_session_type': {
                        'id_sites': [10],
                        'session_type': {
                            'id_session_type': 0,
                            'session_type_name': 'Test Session Type',
                            'session_type_online': True,
                            'session_type_config': '',
                            'session_type_color': '#FF0000',
                            'session_type_category': 1,  #Service
                    }
                }
            }
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, params=None, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_post_endpoint_with_valid_schema_create_session_type_with_inaccessible_projects(self):
        with self._flask_app.app_context():

            json_data = {'service_session_type': {
                        'id_projects': [10],
                        'session_type': {
                            'id_session_type': 0,
                            'session_type_name': 'Test Session Type',
                            'session_type_online': True,
                            'session_type_config': '',
                            'session_type_color': '#FF0000',
                            'session_type_category': 1,  #Service
                    }
                }
            }
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, params=None, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_post_endpoint_with_valid_schema_create_session_type_with_inaccessible_participants(self):
        with self._flask_app.app_context():

            json_data = {'service_session_type': {
                        'id_participants': [10],
                        'session_type': {
                            'id_session_type': 0,
                            'session_type_name': 'Test Session Type',
                            'session_type_online': True,
                            'session_type_config': '',
                            'session_type_color': '#FF0000',
                            'session_type_category': 1,  #Service
                    }
                }
            }
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, params=None, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_post_endpoint_with_valid_schema_new_session_and_valid_sites(self):
        with self._flask_app.app_context():

            json_data = {'service_session_type': {
                        'id_sites': [1],
                        'session_type': {
                            'id_session_type': 0,
                            'session_type_name': 'Test Session Type',
                            'session_type_online': True,
                            'session_type_config': '',
                            'session_type_color': '#FF0000',
                            'session_type_category': 1,  #Service
                    }
                }
            }
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=json_data, params=None, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)