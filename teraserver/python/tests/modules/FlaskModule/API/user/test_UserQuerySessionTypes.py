from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraSession import TeraSession
import datetime


class UserQuerySessionTypesTest(BaseUserAPITest):
    test_endpoint = '/api/user/sessiontypes'

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
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = TeraSessionType.get_count()
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(data_item)

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="list=1")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = TeraSessionType.get_count()
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_session_type=1")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_specific_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params="id_session_type=1")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params="id_session_type=1")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_specific_project_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_project=3")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_project=1&list=1")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = TeraSessionTypeProject.get_count({'id_project': 1})
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_project_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params="id_project=1")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params="id_project=1&list=1")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = TeraSessionTypeProject.get_count({'id_project': 1})
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_site_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_site=2")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params="id_site=1&list=1")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = TeraSessionTypeSite.get_count(filters={'id_site': 1})
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_site_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params="id_site=2")
            self.assertEqual(403, response.status_code)

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params="id_site=1")
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = TeraSessionTypeSite.get_count(filters={'id_site': 1})
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                'id_service': None,
                'session_type_category': 1,
                'session_type_color': 'red',
                'session_type_name': 'Test',
                'session_type_online': True
                }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing session_type")

            # New with minimal infos
            json_data = {
                'session_type': {
                    'session_type_category': 1,
                    'session_type_color': 'red',
                    'session_type_name': 'Test',
                    'session_type_online': True
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_session_type")  # Missing id_session_type

            json_data['session_type']['id_session_type'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service")  # Missing id_service

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Post new, bad service project association")

            json_data['session_type']['id_service'] = 3
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing session_type_sites for siteadmin")

            json_data['session_type']['session_type_sites'] = [{'id_site': 1}]
            json_data['session_type']['session_type_projects'] = [{'id_project': 1}, {'id_project': 3}]
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to project!")

            json_data['session_type']['session_type_sites'] = [{'id_site': 2}]
            json_data['session_type']['session_type_projects'] = [{'id_project': 1}, {'id_project': 2}]
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to site")

            json_data['session_type']['session_type_sites'] = [{'id_site': 1}]
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post OK")

            json_data = response.json[0]
            self._checkJson(json_data)
            current_id = json_data['id_session_type']

            json_data = {
                'session_type': {
                    'id_session_type': current_id,
                    'session_type_category': 2,
                    'session_type_name': 'Test 2',
                    'session_type_projects': [{'id_project': 1}]
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post update")
            self.assertGreater(len(response.json), 0)
            reply_data = response.json[0]
            self._checkJson(reply_data)
            self.assertEqual(reply_data['session_type_name'], 'Test 2')
            self.assertEqual(reply_data['session_type_category'], 2)

            # Check that the untouched project is still there
            stp = TeraSessionTypeProject.get_projects_for_session_type(current_id)
            self.assertEqual(1, len(stp))

            json_data['session_type']['session_type_projects'] = [{'id_project': 1}, {'id_project': 2}]
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Changed projects")

            # Check that the untouched project is still there
            stp = TeraSessionTypeProject.get_projects_for_session_type(current_id)
            self.assertEqual(2, len(stp))

            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params={'id': current_id})
            self.assertEqual(403, response.status_code, msg="Delete denied")

            # Create a session of that type
            json_session = {'id_session_type': current_id,
                            'session_name': 'Session Test',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            }
            new_session = TeraSession()
            new_session.from_json(json_session)
            TeraSession.insert(new_session)

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params={'id': current_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete because session of that type exists")

            TeraSession.delete(new_session.id_session)

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params={'id': current_id})
            self.assertEqual(200, response.status_code, msg="Delete OK")

            # Remove created project-service association
            sp = TeraServiceProject.get_service_project_for_service_project(project_id=3, service_id=3)
            TeraServiceProject.delete(sp.id_service_project)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_session_type'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('session_type_category'))
        self.assertTrue(json_data.__contains__('session_type_name'))
        self.assertTrue(json_data.__contains__('session_type_color'))
        if not minimal:
            self.assertTrue(json_data.__contains__('session_type_config'))
            self.assertTrue(json_data.__contains__('session_type_online'))
