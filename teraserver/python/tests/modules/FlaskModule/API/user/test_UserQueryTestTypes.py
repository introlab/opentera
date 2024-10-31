from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraTestType import TeraTestType
import datetime


class UserQueryTestTypesTest(BaseUserAPITest):
    test_endpoint = '/api/user/testtypes'

    def setUp(self):
        super().setUp()

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
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(data_item)

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_as_admin_with_id(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_test_type': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_specific_as_admin_with_uuid(self):
        with self._flask_app.app_context():
            test_type = TeraTestType.get_test_type_by_id(1)
            self.assertIsNotNone(test_type)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'test_type_uuid': test_type.test_type_uuid})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_specific_as_admin_with_invalid_id(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_test_type': 1000})
            self.assertEqual(404, response.status_code)

    def test_query_specific_as_admin_with_invalid_uuid(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'test_type_uuid': 'invalid'})
            self.assertEqual(404, response.status_code)

    def test_query_specific_as_admin_with_invalid_key(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'test_type_key': 'invalid'})
            self.assertEqual(404, response.status_code)

    def test_query_as_admin_with_invalid_project(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1000})
            self.assertEqual(403, response.status_code)


    def test_query_specific_project_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 2})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1, 'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_site_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 2})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1, 'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_site_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'id_site': 2})
            self.assertEqual(403, response.status_code)

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {
                'test_type': {
                    'test_type_name': 'Test'
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_test_type")

            json_data['test_type']['id_test_type'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Missing id_service")

            json_data['test_type']['id_service'] = 3
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing test_type_projects for siteadmin")

            json_data['test_type']['test_type_sites'] = [{'id_site': 1}]
            json_data['test_type']['test_type_projects'] = [{'id_project': 1}, {'id_project': 3}]
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to project!")

            json_data['test_type']['test_type_sites'] = [{'id_site': 2}]
            json_data['test_type']['test_type_projects'] = [{'id_project': 1}, {'id_project': 2}]
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to site")

            json_data['test_type']['test_type_sites'] = [{'id_site': 1}]
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post OK")

            json_data = response.json[0]
            self._checkJson(json_data)
            current_id = json_data['id_test_type']

            json_data = {
                'test_type': {
                    'id_test_type': current_id,
                    'test_type_name': 'Test 2',
                    'test_type_has_json_format': True
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post update")
            reply_data = response.json[0]
            self._checkJson(reply_data)
            self.assertEqual(reply_data['test_type_name'], 'Test 2')
            self.assertEqual(reply_data['test_type_has_json_format'], True)

            json_data['test_type']['test_type_projects'] = [{'id_project': 1}]
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Changed projects")

            # Check that the untouched project is still there
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_test_type': current_id},
                                                     endpoint='/api/user/testtypes/projects')
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params={'id': current_id})
            self.assertEqual(403, response.status_code, msg="Delete denied")

            # Create a test of that type
            test = TeraTest()
            test.id_test_type = current_id
            test.test_name = 'Test Test'
            test.test_datetime = datetime.datetime.now()
            test.id_session = 1
            TeraTest.insert(test)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': current_id})
            self.assertEqual(response.status_code, 500, msg="Has associated tests")

            TeraTest.delete(test.id_test)
            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params={'id': current_id})
            self.assertEqual(200, response.status_code, msg="Delete OK")

            # Remove created project-service association
            params = {'id_project': 3}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params,
                                                     endpoint='/api/user/services/projects')
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            id_service_project = response.json[0]['id_service_project']

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': id_service_project},
                                                        endpoint='/api/user/services/projects')
            self.assertEqual(200, response.status_code, msg='Back to default state!')

    def test_query_with_urls(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'with_urls': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(data_item)
                self.assertTrue(data_item.__contains__('test_type_json_url'))
                self.assertTrue(data_item.__contains__('test_type_web_url'))
                self.assertTrue(data_item.__contains__('test_type_web_editor_url'))
                self.assertTrue(data_item.__contains__('access_token'))

    def test_query_access_token_only(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'with_only_token': True})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self.assertEqual(2, len(data_item))
                self.assertTrue(data_item.__contains__('test_type_uuid'))
                self.assertTrue(data_item.__contains__('access_token'))

    def test_query_test_type_by_key(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'test_type_key': 'PRE'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(data_item)
                self.assertEqual(data_item['test_type_key'], 'PRE')

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
