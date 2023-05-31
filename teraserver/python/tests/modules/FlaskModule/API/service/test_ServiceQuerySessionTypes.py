from typing import List
from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraParticipant import TeraParticipant


class ServiceQuerySessionTypesTest(BaseServiceAPITest):
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
