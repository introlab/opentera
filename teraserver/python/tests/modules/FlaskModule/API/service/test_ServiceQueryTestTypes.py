from typing import List
from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraParticipant import TeraParticipant


class ServiceQueryTestTypesTest(BaseServiceAPITest):
    test_endpoint = '/api/service/testtypes'

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

            test_types: List[TeraTestType] = TeraTestType.query.all()
            service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
            from modules.DatabaseModule.DBManager import DBManager
            service_access = DBManager.serviceAccess(service)
            accessible_types = service_access.get_accessible_tests_types()
            self.assertEqual(len(accessible_types), len(response.json))
            self.assertTrue(len(accessible_types) <= len(test_types))
            for test_type in accessible_types:
                json_value = test_type.to_json()
                self.assertTrue(json_value in response.json)

    def test_get_endpoint_with_token_auth_for_site(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params={'id_site': 1}, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)

            test_types: List[TeraTestType] = [tt.test_type_site_test_type for tt in
                                              TeraTestTypeSite.get_tests_types_for_site(1)]
            service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
            from modules.DatabaseModule.DBManager import DBManager
            service_access = DBManager.serviceAccess(service)
            accessible_types = service_access.get_accessible_tests_types()
            self.assertEqual(len(accessible_types), len(response.json))
            self.assertTrue(len(accessible_types) <= len(test_types))
            for test_type in accessible_types:
                json_value = test_type.to_json()
                self.assertTrue(json_value in response.json)

    def test_get_endpoint_with_token_auth_for_project(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params={'id_project': 1}, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)

            test_types: List[TeraTestType] = [tt.test_type_project_test_type for tt in
                                              TeraTestTypeProject.get_tests_types_for_project(1)]
            service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
            from modules.DatabaseModule.DBManager import DBManager
            service_access = DBManager.serviceAccess(service)
            accessible_types = service_access.get_accessible_tests_types()
            self.assertEqual(len(accessible_types), len(response.json))
            self.assertTrue(len(accessible_types) <= len(test_types))
            for test_type in accessible_types:
                json_value = test_type.to_json()
                self.assertTrue(json_value in response.json)

    def test_get_endpoint_with_token_auth_for_participant(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params={'id_participant': 1}, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)

            project_id = TeraParticipant.get_participant_by_id(1).id_project
            test_types: List[TeraTestType] = [tt.test_type_project_test_type for tt in
                                              TeraTestTypeProject.get_tests_types_for_project(project_id)]
            service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
            from modules.DatabaseModule.DBManager import DBManager
            service_access = DBManager.serviceAccess(service)
            accessible_types = service_access.get_accessible_tests_types()
            self.assertEqual(len(accessible_types), len(response.json))
            self.assertTrue(len(accessible_types) <= len(test_types))
            for test_type in accessible_types:
                json_value = test_type.to_json()
                self.assertTrue(json_value in response.json)

    def test_get_endpoint_with_token_auth_for_id(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params={'id_test_type': 1}, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)

            service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
            from modules.DatabaseModule.DBManager import DBManager
            service_access = DBManager.serviceAccess(service)
            accessible_types = service_access.get_accessible_tests_types_ids()
            self.assertEqual(1, len(response.json))
            self.assertTrue(response.json[0]['id_test_type'] in accessible_types)
            self.assertEqual(response.json[0]['id_test_type'], 1)

    def test_get_endpoint_with_token_auth_for_key(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params={'test_type_key': 'PRE'}, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)

            test_types: List[TeraTestType] = [TeraTestType.get_test_type_by_key('PRE')]
            service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
            from modules.DatabaseModule.DBManager import DBManager
            service_access = DBManager.serviceAccess(service)
            accessible_types = service_access.get_accessible_tests_types_ids()
            self.assertEqual(1, len(response.json))
            self.assertTrue(response.json[0]['id_test_type'] in accessible_types)
            self.assertEqual(response.json[0]['id_test_type'], test_types[0].id_test_type)
