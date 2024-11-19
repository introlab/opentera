from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
import datetime


class UserQueryTestTypeProjectTest(BaseUserAPITest):
    test_endpoint = '/api/user/testtypes/projects'

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

    def test_query_as_admin_with_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(400, response.status_code)

    def test_query_as_user_with_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user')
            self.assertEqual(400, response.status_code)

    def test_query_project_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 10}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json), 0)

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_project_with_test_type_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 2, 'with_tests_types': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_test_type_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 30}  # Invalid
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_test_type': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_test_type_with_projects_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 1, 'with_projects': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_test_type_with_projects_and_with_sites_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 3, 'with_projects': 1, 'with_sites': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_site'))
                self.assertTrue(data_item.__contains__('site_name'))

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'list': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 2)

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_project_as_user(self):
        with self._flask_app.app_context():
            params = {'id_project': 10}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_project_with_test_type_as_user(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'with_test_type': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_test_type_as_user(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 30}  # Invalid
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_test_type': 4}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_test_type': 2}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_test_type_with_projects_as_user(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 1, 'with_projects': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 2, 'list': 1}

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_post_test_type(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing everything")  # Missing

            json_data = {'test_type': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_test_type")

            json_data = {'test_type': {'id_test_type': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing projects")

            json_data = {'test_type': {'id_test_type': 1, 'projects': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only project/site admins can change things here")

            json_data = {'test_type': {'id_test_type': 3, 'projects': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove from all projects OK")

            params = {'id_test_type': 3}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            json_data = {'test_type': {'id_test_type': 3, 'projects': [{'id_project': 1},
                                                                       {'id_project': 2},
                                                                       {'id_project': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="One project not part of session type site")

            json_data = {'test_type': {'id_test_type': 3, 'projects': [{'id_project': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all projects OK")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))  # Everything was added

            json_data = {'test_type': {'id_test_type': 1, 'projects': [{'id_project': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove one project")
            self.assertIsNone(TeraTestTypeProject.get_test_type_project_for_test_type_project(project_id=3,
                                                                                              test_type_id=1))
            self.assertIsNone(TeraTestTypeProject.get_test_type_project_for_test_type_project(project_id=2,
                                                                                              test_type_id=1))
            self.assertIsNotNone(TeraTestTypeProject.get_test_type_project_for_test_type_project(project_id=1,
                                                                                                 test_type_id=1))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            json_data = {'test_type': {'id_test_type': 1, 'projects': [{'id_project': 1},
                                                                       {'id_project': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Back to initial")

    def test_post_project(self):
        with self._flask_app.app_context():
            # Create test types and associate in the db for this test
            json_testtype = {
                'test_type_name': 'Test Type',
                'id_service': 1
            }
            testtype1 = TeraTestType()
            testtype1.from_json(json_testtype)
            TeraTestType.insert(testtype1)

            testtype2 = TeraTestType()
            testtype2.from_json(json_testtype)
            TeraTestType.insert(testtype2)

            tts1 = TeraTestTypeSite()
            tts1.id_test_type = testtype1.id_test_type
            tts1.id_site = 1
            TeraTestTypeSite.insert(tts1)

            tts2 = TeraTestTypeSite()
            tts2.id_test_type = testtype2.id_test_type
            tts2.id_site = 1
            TeraTestTypeSite.insert(tts2)

            ttp1 = TeraTestTypeProject()
            ttp1.id_test_type = testtype1.id_test_type
            ttp1.id_project = 2
            TeraTestTypeProject.insert(ttp1)

            ttp2 = TeraTestTypeProject()
            ttp2.id_test_type = testtype2.id_test_type
            ttp2.id_project = 2
            TeraTestTypeProject.insert(ttp2)

            # Project update
            json_data = {}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing project")

            json_data = {'project': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_project")

            json_data = {'project': {'id_project': 2}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing test types")

            json_data = {'project': {'id_project': 2, 'testtypes': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only project admins can change things here")

            json_data = {'project': {'id_project': 2, 'testtypes': []}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove all test types OK")

            params = {'id_project': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            json_data = {'project': {'id_project': 2, 'testtypes': [{'id_test_type': testtype1.id_test_type},
                                                                    {'id_test_type': testtype2.id_test_type},
                                                                    {'id_test_type': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="One test type not allowed - not part of the site project!")

            json_data = {'project': {'id_project': 2, 'testtypes': [{'id_test_type': testtype1.id_test_type},
                                                                    {'id_test_type': testtype2.id_test_type}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="New test type association OK")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))  # Everything was added

            json_data = {'project': {'id_project': 2, 'testtypes': [{'id_test_type': testtype1.id_test_type}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove 1 type")
            self.assertIsNotNone(TeraTestTypeProject.
                                 get_test_type_project_for_test_type_project(project_id=2,
                                                                             test_type_id=testtype1.id_test_type))
            self.assertIsNone(TeraTestTypeProject.
                              get_test_type_project_for_test_type_project(project_id=2,
                                                                          test_type_id=testtype2.id_test_type))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            # Delete all created for that test
            TeraTestTypeSite.delete(tts1.id_test_type_site)
            TeraTestTypeSite.delete(tts2.id_test_type_site)
            TeraTestType.delete(testtype1.id_test_type)
            TeraTestType.delete(testtype2.id_test_type)

    def test_post_test_type_project_and_delete(self):
        with self._flask_app.app_context():
            # TestType-Project update
            json_data = {'test_type_project': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'test_type_project': {'id_project': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'test_type_project': {'id_project': 1, 'id_test_type': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only project admins can change things here")

            json_data = {'test_type_project': {'id_project': 1, 'id_test_type': 3}}
            response = self._post_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Add new association not OK - type not part of the site")

            json_data = {'test_type_project': {'id_project': 2, 'id_test_type': 2}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add new association OK")

            params = {'id_project': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)

            current_id = None
            for dp in response.json:
                if dp['id_test_type'] == 2:
                    current_id = dp['id_test_type_project']
                    break
            self.assertFalse(current_id is None)

            response = self._delete_with_user_http_auth(self.test_client, username='user', password='user',
                                                        params={'id': current_id})
            self.assertEqual(403, response.status_code, msg="Delete denied")

            # Create a test of that type for a session
            project = TeraProject.get_project_by_id(2)
            json_data = {
                'id_participant': 0,
                'id_project': project.id_project,
                'participant_name': 'Test Participant'
            }

            participant = TeraParticipant()
            participant.from_json(json_data)
            TeraParticipant.insert(participant)

            json_session = {'id_session_type': 1,
                            'session_name': 'Session',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            'id_creator_participant': participant.id_participant
                            }
            session = TeraSession()
            session.from_json(json_session)
            TeraSession.insert(session)

            json_session = {'id_session_type': 1,
                            'session_name': 'Session 2',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0
                            }
            session2 = TeraSession()
            session2.from_json(json_session)
            TeraSession.insert(session2)

            ses_participant = TeraSessionParticipants()
            ses_participant.id_participant = participant.id_participant
            ses_participant.id_session = session2.id_session
            TeraSessionParticipants.insert(ses_participant)

            json_test = {'id_test_type': 2,
                         'id_session': session.id_session,
                         'test_name': 'Test Participant',
                         'test_datetime': datetime.datetime.now()
                         }
            new_test = TeraTest()
            new_test.from_json(json_test)
            TeraTest.insert(new_test)

            json_test['id_session'] = session2.id_session
            new_test2 = TeraTest()
            new_test2.from_json(json_test)
            TeraTest.insert(new_test2)

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params={'id': current_id})
            self.assertEqual(500, response.status_code, msg="Has tests of that type, can't delete")

            TeraTest.delete(new_test.id_test)

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params={'id': current_id})
            self.assertEqual(500, response.status_code, msg="Has tests of that type, can't delete")

            TeraSession.delete(session.id_session)
            TeraTest.delete(new_test2.id_test)

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params={'id': current_id})
            self.assertEqual(200, response.status_code, msg="Delete OK")

            TeraSession.delete(session2.id_session)
            TeraParticipant.delete(participant.id_participant)

            params = {'id_project': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(TeraTestTypeProject.query.filter_by(id_project=2).count(), len(response.json))

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_test_type_project'))
        self.assertTrue(json_data.__contains__('id_test_type'))
        self.assertTrue(json_data.__contains__('id_project'))

        if not minimal:
            self.assertTrue(json_data.__contains__('test_type_name'))
            self.assertTrue(json_data.__contains__('project_name'))
        else:
            self.assertFalse(json_data.__contains__('test_type_name'))
            self.assertFalse(json_data.__contains__('project_name'))
