from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from datetime import datetime


class ServiceQueryTestsTest(BaseServiceAPITest):
    test_endpoint = '/api/service/tests'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import service_api_ns
        from BaseServiceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.service.ServiceQueryTests import ServiceQueryTests
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseServiceAPITest.getConfig())}
        service_api_ns.add_resource(ServiceQueryTests, '/tests', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        response = self.test_client.get(self.test_endpoint)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=None, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code)

    def test_post_endpoint_no_auth(self):
        response = self.test_client.post(self.test_endpoint)
        self.assertEqual(401, response.status_code)

    def test_delete_endpoint_no_auth(self):
        params = {'uuid': 0}
        response = self.test_client.delete(self.test_endpoint, query_string=params)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_query_no_params(self):
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=None, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code)

    def test_get_endpoint_query_bad_params(self):
        params = {'id_invalid': 1}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 400)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_test'))
        self.assertTrue(json_data.__contains__('id_session'))
        self.assertTrue(json_data.__contains__('id_device'))
        self.assertTrue(json_data.__contains__('id_participant'))
        self.assertTrue(json_data.__contains__('id_user'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('test_name'))
        self.assertTrue(json_data.__contains__('test_uuid'))
        self.assertTrue(json_data.__contains__('test_datetime'))
        if not minimal:
            self.assertTrue(json_data.__contains__('test_answers_url'))
            self.assertTrue(json_data.__contains__('test_answers_web_url'))
            self.assertTrue(json_data.__contains__('access_token'))

    def test_get_endpoint_query_tests_by_service_uuid(self):
        params = {'service_uuid': self.service_uuid, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_device_tests(self):
        params = {'id_device': 1, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json), 1)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_device_tests_no_access(self):
        params = {'id_device': 4, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_endpoint_query_session_tests(self):
        params = {'id_session': 2}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)

        for data_item in response.json:
            self._checkJson(json_data=data_item, minimal=True)

    def test_get_endpoint_query_session_tests_no_access(self):
        params = {'id_session': 100}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_endpoint_query_participant_tests(self):
        params = {'id_participant': 1, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json), 3)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_participant_tests_no_access(self):
        params = {'id_participant': 4, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_endpoint_query_user_tests(self):
        params = {'id_user': 2, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_user_tests_no_access(self):
        params = {'id_user': 6, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 403)

    def test_get_endpoint_query_tests(self):
        params = {'id_test': 1, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json), 1)

        for data_item in response.json:
            self._checkJson(json_data=data_item)

    def test_get_endpoint_query_test_no_access(self):
        params = {'id_test': 5, 'with_urls': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

    def test_post_endpoint_with_update_and_delete(self):
        # New with minimal infos
        json_data = {
            'test': {
                'test_name': 'Test Test',
                'test_datetime': datetime.now().isoformat()}
        }

        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=json_data, endpoint=self.test_endpoint)

        self.assertEqual(400, response.status_code, msg="Missing id_test")

        json_data['test']['id_test'] = 0
        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=json_data, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code, msg="Missing test type")

        json_data['test']['id_test_type'] = 1
        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=json_data, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code, msg="Missing id_session")

        json_data['test']['id_session'] = 1
        # response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
        #                                               json=json_data, endpoint=self.test_endpoint)
        # self.assertEqual(403, response.status_code, msg="Test type not accessible to this service")

        # json_data['test']['id_test_type'] = 1
        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=json_data, endpoint=self.test_endpoint)
        self.assertEqual(200, response.status_code, msg="Post new")  # All ok now!

        json_data = response.json[0]
        self._checkJson(json_data, minimal=True)
        current_id = json_data['id_test']
        current_uuid = json_data['test_uuid']

        json_data = {
            'test': {
                'id_test': current_id,
                'test_name': 'Test Test 2'
            }
        }

        response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                      json=json_data, endpoint=self.test_endpoint)
        self.assertEqual(200, response.status_code, msg="Post update")
        json_data = response.json[0]
        self._checkJson(json_data, minimal=True)
        self.assertEqual(json_data['test_name'], 'Test Test 2')

        # Delete
        response = self._delete_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                        params={'uuid': current_uuid}, endpoint=self.test_endpoint)

        self.assertEqual(200, response.status_code, msg="Delete OK")

        # Bad delete
        response = self._delete_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                        params={'uuid': current_uuid}, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code, msg="Wrong delete")

    def test_get_endpoint_query_session_tests_as_admin_token_only(self):
        params = {'id_session': 2, 'with_urls': True, 'with_only_token': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)
        for data_item in response.json:
            self.assertFalse(data_item.__contains__("test_name"))
            self.assertTrue(data_item.__contains__("test_uuid"))
            self.assertTrue(data_item.__contains__("access_token"))
