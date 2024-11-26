from typing import List
from tests.modules.FlaskModule.API.service.BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraTest import TeraTest
import datetime


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

    def test_post_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint, query_string=None, headers=None, json={})
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

    def test_get_endpoint_with_token_auth_for_uuid(self):
        with self._flask_app.app_context():

            all_test_types = TeraTestType.query.all()
            service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
            for test_type in all_test_types:
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params={'test_type_uuid': test_type.test_type_uuid},
                                                             endpoint=self.test_endpoint)
                self.assertEqual(200, response.status_code)

                # Check if test type is accessible
                from modules.DatabaseModule.DBManager import DBManager
                service_access = DBManager.serviceAccess(service)
                accessible_types = service_access.get_accessible_tests_types_ids()
                if test_type.id_test_type in accessible_types:
                    self.assertEqual(1, len(response.json))
                    self.assertEqual(response.json[0]['id_test_type'], test_type.id_test_type)
                    self.assertEqual(response.json[0]['test_type_uuid'], test_type.test_type_uuid)


    def test_get_endpoint_with_token_auth_for_invalid_uuid(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params={'test_type_uuid': '0000000000000000'},
                                                         endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))


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

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {
                'test_type': {
                    'test_type_name': 'Test'
                }
            }

            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_test_type")

            json_data['test_type']['id_test_type'] = 0
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="New OK")

            json_data = response.json
            self._checkJson(json_data)
            current_id = json_data['id_test_type']
            current_uuid = json_data['test_type_uuid']

            json_data = {
                'test_type': {
                    'id_test_type': 3,
                    'test_type_name': 'Test 2',
                    'test_type_has_json_format': True
                }
            }

            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to test type")

            json_data['test_type']['id_test_type'] = current_id
            json_data['test_type']['id_service'] = 1
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(403, response.status_code, msg="Not current service")

            del json_data['test_type']['id_service']
            response = self._post_with_service_token_auth(self.test_client, token=self.service_token, json=json_data)
            self.assertEqual(200, response.status_code, msg="Update OK")

            reply_data = response.json
            self._checkJson(reply_data)
            self.assertEqual(reply_data['test_type_name'], 'Test 2')
            self.assertEqual(reply_data['test_type_has_json_format'], True)

            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'uuid': '0000000000000000'})
            self.assertEqual(400, response.status_code, msg="Bad parameter")

            test_type: TeraTestType = TeraTestType.get_test_type_by_id(3)
            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'uuid': test_type.test_type_uuid})
            self.assertEqual(403, response.status_code, msg="No access to test type")

            # Create a test of that type
            test = TeraTest()
            test.id_test_type = current_id
            test.test_name = 'Test Test'
            test.test_datetime = datetime.datetime.now()
            test.id_session = 1
            TeraTest.insert(test)

            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'uuid': current_uuid})
            self.assertEqual(response.status_code, 500, msg="Has associated tests")

            TeraTest.delete(test.id_test)
            response = self._delete_with_service_token_auth(self.test_client, token=self.service_token,
                                                            params={'uuid': current_uuid})
            self.assertEqual(200, response.status_code, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_test_type'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('test_type_uuid'))
        self.assertTrue(json_data.__contains__('test_type_name'))
        self.assertTrue(json_data.__contains__('test_type_key'))
        self.assertTrue(json_data.__contains__('test_type_has_json_format'))
        self.assertTrue(json_data.__contains__('test_type_has_web_format'))
        self.assertTrue(json_data.__contains__('test_type_has_web_editor'))
        if not minimal:
            self.assertTrue(json_data.__contains__('test_type_description'))
            self.assertTrue(json_data.__contains__('test_type_service_key'))
            self.assertTrue(json_data.__contains__('test_type_service_uuid'))
