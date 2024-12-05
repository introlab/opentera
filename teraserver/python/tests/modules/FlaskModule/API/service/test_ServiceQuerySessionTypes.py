from typing import List
from tests.modules.FlaskModule.API.service.BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSessionTypeServices import TeraSessionTypeServices
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

    def test_get_specific_forbidden(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 4}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg='No access to session type')
            self.assertEqual(0, len(response.json))

    def test_get_specific_allowed_because_creator(self):
        with self._flask_app.app_context():
            params = {'id_session_type': 1}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code, msg='Get OK')
            self.assertEqual(1, len(response.json))

    def test_get_specific_allowed_because_secondary(self):
        with self._flask_app.app_context():
            service: TeraService = TeraService.get_service_by_key('FileTransferService')
            token = service.get_token(self.service_key)
            for sts in TeraSessionTypeServices.get_sessions_types_for_service(service.id_service):
                params = {'id_session_type': sts.id_session_type}
                response = self._get_with_service_token_auth(client=self.test_client, token=token,
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
            self.assertTrue('id_session_type' in response.json)
            id_session_type = response.json['id_session_type']

            # Check if session type was created
            session_type = TeraSessionType.get_session_type_by_id(id_session_type)
            self.assertIsNotNone(session_type)

            # Check if session type was linked to site
            sites = TeraSessionTypeSite.get_sites_for_session_type(id_session_type)
            self.assertIsNotNone(sites)
            self.assertEqual(1, len(sites))
            self.assertEqual(sites[0].id_site, 1)


    def test_post_endpoint_with_valid_schema_new_session_and_valid_projects(self):
        with self._flask_app.app_context():

            json_data = {'service_session_type': {
                        'id_projects': [1],
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
            self.assertTrue('id_session_type' in response.json)
            id_session_type = response.json['id_session_type']

            # Check if session type was created
            session_type = TeraSessionType.get_session_type_by_id(id_session_type)
            self.assertIsNotNone(session_type)

            # Check if session type was linked to project
            projects = TeraSessionTypeProject.get_projects_for_session_type(id_session_type)
            self.assertIsNotNone(projects)
            self.assertEqual(1, len(projects))
            self.assertEqual(projects[0].id_project, 1)

    def test_post_endpoint_with_valid_schema_new_session_and_valid_participants(self):
        with self._flask_app.app_context():

            json_data = {'service_session_type': {
                        'id_participants': [1],
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
            self.assertTrue('id_session_type' in response.json)
            id_session_type = response.json['id_session_type']

            # Check if session type was created
            session_type = TeraSessionType.get_session_type_by_id(id_session_type)
            self.assertIsNotNone(session_type)

            # Check if session type was linked to project
            participant = TeraParticipant.get_participant_by_id(1)
            projects = TeraSessionTypeProject.get_projects_for_session_type(participant.id_project)
            self.assertIsNotNone(projects)
            self.assertEqual(1, len(projects))
            self.assertEqual(projects[0].id_project, participant.id_project)
