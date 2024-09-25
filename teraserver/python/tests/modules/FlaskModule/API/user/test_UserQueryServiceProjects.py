from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraSession import TeraSession
import datetime


class UserQueryServiceProjectsTest(BaseUserAPITest):
    test_endpoint = '/api/user/services/projects'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_no_auth(self):
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
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params="")
            self.assertEqual(400, response.status_code)

    def test_query_project_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 10}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_project_with_services_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'with_services': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_service_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_service': 30}  # Invalid service
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_service': 5}  # Videorehab service
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_service_with_projects_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_service': 3, 'with_projects': 1}  # File transfer service
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_service_with_projects_and_with_sites_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_service': 3, 'with_projects': 1, 'with_sites': 1}  # File transfer service
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_site'))
                self.assertTrue(data_item.__contains__('site_name'))

    def test_query_service_with_roles_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_service': 5, 'with_roles': 1}  # Videorehab service
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('service_roles'))

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'list': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

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

    def test_query_project_with_services_as_user(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'with_services': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(3, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_service_as_user(self):
        with self._flask_app.app_context():
            params = {'id_service': 30}  # Invalid service
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_service': 3}  # File transfer service
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_service': 5}  # Videorehab service
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_service_with_projects_as_user(self):
        with self._flask_app.app_context():
            params = {'id_service': 5, 'with_projects': 1}  # Videorehab service
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        with self._flask_app.app_context():
            params = {'id_service': 5, 'list': 1}

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

    def test_post_service(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing everything")  # Missing

            # Service update
            json_data = {'service': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service")

            json_data = {'service': {'id_service': 3}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing projects")

            json_data = {'service': {'id_service': 3, 'projects': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only super admins can change things here")

            json_data = {'service': {'id_service': 3, 'projects': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove from all projects OK")

            params = {'id_service': 3}  # File transfer service
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            json_data = {'service': {'id_service': 3, 'projects': [{'id_project': 1},
                                                                   {'id_project': 2},
                                                                   {'id_project': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all projects OK")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(3, len(response.json))  # Everything was added

            json_data = {'service': {'id_service': 3, 'projects': [{'id_project': 1},
                                                                   {'id_project': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove one project")
            self.assertIsNotNone(TeraServiceProject.get_service_project_for_service_project(project_id=2, service_id=3))
            self.assertIsNotNone(TeraServiceProject.get_service_project_for_service_project(project_id=1, service_id=3))
            self.assertIsNone(TeraServiceProject.get_service_project_for_service_project(project_id=3, service_id=3))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))  # Back to the default state

            # Recreate default associations - session types
            json_data = {'session_type_project': [{'id_session_type': 1, 'id_project': 1},
                                                  {'id_session_type': 2, 'id_project': 1},
                                                  {'id_session_type': 3, 'id_project': 1},
                                                  {'id_session_type': 4, 'id_project': 1},
                                                  {'id_session_type': 5, 'id_project': 1}]}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data,
                                                      endpoint='/api/user/sessiontypes/projects')
            self.assertEqual(200, response.status_code)

    def test_post_project(self):
        with self._flask_app.app_context():
            # Project update
            json_data = {'project': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_project")

            json_data = {'project': {'id_project': 2}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing services")

            json_data = {'project': {'id_project': 2, 'services': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only site admins can change things here")

            json_data = {'project': {'id_project': 2, 'services': []}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove all services OK")

            params = {'id_project': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            json_data = {'project': {'id_project': 2, 'services': [{'id_service': 2},
                                                                   {'id_service': 3},
                                                                   {'id_service': 4},
                                                                   {'id_service': 5}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="One service not allowed - not part of the site project!")

            json_data = {'project': {'id_project': 2, 'services': [{'id_service': 2},
                                                                   {'id_service': 3},
                                                                   {'id_service': 5}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="New service association OK")
            self.assertIsNone(TeraServiceProject.get_service_project_for_service_project(project_id=2, service_id=4))
            self.assertIsNotNone(TeraServiceProject.get_service_project_for_service_project(project_id=2, service_id=2))
            self.assertIsNotNone(TeraServiceProject.get_service_project_for_service_project(project_id=2, service_id=3))
            self.assertIsNotNone(TeraServiceProject.get_service_project_for_service_project(project_id=2, service_id=5))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(3, len(response.json))  # Everything was added

            json_data = {'project': {'id_project': 2, 'services': [{'id_service': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove 1 service")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))  # Back to the default state

    def test_post_service_project_and_delete(self):
        with self._flask_app.app_context():
            # Service-Project update
            json_data = {'service_project': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'service_project': {'id_project': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'service_project': {'id_project': 1, 'id_service': 4}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only site admins can change things here")

            json_data = {'service_project': {'id_project': 1, 'id_service': 4}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Add new association not OK - project not part of the site")

            json_data = {'service_project': {'id_project': 1, 'id_service': 2}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add new association OK")

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(3, len(response.json))

            current_id = None
            for sp in response.json:
                if sp['id_service'] == 2:
                    current_id = sp['id_service_project']
                    break
            self.assertFalse(current_id is None)

            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user', password='user',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params=params)
            self.assertEqual(200, response.status_code, msg="Delete OK")

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))  # Back to initial state!

            # Recreate default associations - session types
            json_data = {'session_type_project': [{'id_session_type': 1, 'id_project': 1},
                                                  {'id_session_type': 2, 'id_project': 1},
                                                  {'id_session_type': 3, 'id_project': 1},
                                                  {'id_session_type': 4, 'id_project': 1},
                                                  {'id_session_type': 5, 'id_project': 1}]}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data,
                                                      endpoint='/api/user/sessiontypes/projects')
            self.assertEqual(200, response.status_code)

    def test_service_project_delete_exceptions(self):
        with self._flask_app.app_context():
            # Create 3 sessions: one with asset, one with test and one of the session type of the service
            participant = TeraParticipant.get_participant_by_id(4)  # Participant in Secret Site
            site: TeraSite = TeraSite.get_site_by_id(2)
            project = site.site_projects[0]
            test_type = TeraTestType.get_test_type_by_key("PRE")
            service = TeraService.get_service_by_key("VideoRehabService")

            ss = TeraServiceSite()
            ss.id_site = site.id_site
            ss.id_service = service.id_service
            TeraServiceSite.insert(ss)

            sp = TeraServiceProject()
            sp.id_project = project.id_project
            sp.id_service = service.id_service
            TeraServiceProject.insert(sp)

            sts = TeraSessionTypeSite()
            sts.id_site = site.id_site
            sts.id_session_type = 1  # Videorehab
            TeraSessionTypeSite.insert(sts)

            stp1 = TeraSessionTypeProject()
            stp1.id_project = project.id_project
            stp1.id_session_type = 1
            TeraSessionTypeProject.insert(stp1)

            stp2 = TeraSessionTypeProject()
            stp2.id_project = project.id_project
            stp2.id_session_type = 4
            TeraSessionTypeProject.insert(stp2)

            ttp = TeraTestTypeProject()
            ttp.id_project = project.id_project
            ttp.id_test_type = test_type.id_test_type
            TeraTestTypeProject.insert(ttp)

            json_session = {'id_session_type': 1,
                            'session_name': 'Session of session type',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            'id_creator_participant': participant.id_participant
                            }
            session1 = TeraSession()
            session1.from_json(json_session)
            TeraSession.insert(session1)

            json_session = {'id_session_type': 4,
                            'session_name': 'Session wite test',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            'id_creator_participant': participant.id_participant
                            }

            session2 = TeraSession()
            session2.from_json(json_session)
            TeraSession.insert(session2)

            json_session = {'id_session_type': 4,
                            'session_name': 'Session wite asset',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            'id_creator_participant': participant.id_participant
                            }

            session3 = TeraSession()
            session3.from_json(json_session)
            TeraSession.insert(session3)

            json_test = {'id_test_type': test_type.id_test_type,
                         'id_session': session2.id_session,
                         'test_name': 'Test Test',
                         'test_datetime': datetime.datetime.now()
                         }
            test = TeraTest()
            test.from_json(json_test)
            TeraTest.insert(test)

            json_asset = {'id_session': session3.id_session,
                          'asset_name': "Test asset",
                          'asset_service_uuid': service.service_uuid,
                          'asset_type': "Test",
                          'test_datetime': datetime.datetime.now()
                          }
            asset = TeraAsset()
            asset.from_json(json_asset)
            TeraAsset.insert(asset)

            # All set... let's test!
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': sp.id_service_project})
            self.assertEqual(500, response.status_code, msg='Session of session type')
            TeraSession.delete(session1.id_session)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': sp.id_service_project})
            self.assertEqual(500, response.status_code, msg='Test of test type')
            TeraSession.delete(session2.id_session)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': sp.id_service_project})
            self.assertEqual(500, response.status_code, msg='Asset of service')
            TeraSession.delete(session3.id_session)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': sp.id_service_project})
            self.assertEqual(200, response.status_code, msg='All OK now!')

            # Back to initial state
            TeraServiceSite.delete(ss.id_service_site)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_service_project'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('id_project'))

        if not minimal:
            self.assertTrue(json_data.__contains__('service_name'))
            self.assertTrue(json_data.__contains__('service_key'))
            self.assertTrue(json_data.__contains__('service_system'))
            self.assertTrue(json_data.__contains__('project_name'))
        else:
            self.assertFalse(json_data.__contains__('service_name'))
            self.assertFalse(json_data.__contains__('service_key'))
            self.assertFalse(json_data.__contains__('service_system'))
            self.assertFalse(json_data.__contains__('project_name'))
