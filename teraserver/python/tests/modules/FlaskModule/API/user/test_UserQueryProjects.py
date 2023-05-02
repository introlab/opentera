from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
import datetime


class UserQueryProjectsTest(BaseUserAPITest):
    test_endpoint = '/api/user/projects'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client)
            self.assertEqual(401, response.status_code)

    def test_query_projects_enabled(self):
        with self._flask_app.app_context():
            # Create new project
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'Disabled project'
            new_project.project_enabled = False
            TeraProject.insert(new_project)

            # Query all projects
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(200, response.status_code)
            target_len = TeraProject.get_count()
            self.assertEqual(target_len, len(response.json))

            # Query only enabled
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'enabled': 1})
            self.assertEqual(200, response.status_code)
            target_len = TeraProject.get_count({'project_enabled': True})
            self.assertEqual(target_len, len(response.json))

            # Query only disabled
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'enabled': 0})
            self.assertEqual(200, response.status_code)
            target_len = TeraProject.get_count({'project_enabled': False})
            self.assertEqual(target_len, len(response.json))

            # Delete created project
            TeraProject.delete(new_project.id_project)



    def test_query_specific_project_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self._checkJson(json_data=response.json[0], minimal=False)
            id_project = response.json[0]['id_project']
            name = response.json[0]['project_name']

            # by name
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'name': name})
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self._checkJson(json_data=response.json[0], minimal=False)
            self.assertEqual(response.json[0]['id_project'], id_project)

            # with minimal infos
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1, 'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self._checkJson(json_data=response.json[0], minimal=True)

    def test_query_specific_project_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_project': 1})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(json_data, [])

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'id_project': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self._checkJson(json_data=response.json[0], minimal=False)
            id_project = response.json[0]['id_project']
            name = response.json[0]['project_name']

            # by name
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'name': name})
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self._checkJson(json_data=response.json[0], minimal=False)
            self.assertEqual(response.json[0]['id_project'], id_project)

            # with minimal infos
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'id_project': 1, 'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self._checkJson(json_data=response.json[0], minimal=True)

    def test_query_specific_site(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(json_data, [])

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code)
            target_count = TeraProject.get_count(filters={'id_site': 1})
            self.assertEqual(target_count, len(response.json))
            for part_data in response.json:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_specific_service(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 3})
            self.assertEqual(200, response.status_code)
            target_count = len(TeraServiceProject.get_projects_for_service(3))
            self.assertEqual(target_count, len(response.json))
            for part_data in response.json:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_specific_user_uuid(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('admin')
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'user_uuid': user.user_uuid})
            self.assertEqual(200, response.status_code)
            target_count = len(user.get_projects_roles())
            self.assertEqual(target_count, len(response.json))
            for part_data in response.json:
                self._checkJson(json_data=part_data, minimal=False)

            user = TeraUser.get_user_by_username('user3')
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'user_uuid': user.user_uuid})
            self.assertEqual(200, response.status_code)
            target_count = len(user.get_projects_roles())
            self.assertEqual(target_count, len(response.json))
            for part_data in response.json:
                self._checkJson(json_data=part_data, minimal=False)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                'project_name': 'Testing123',
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing project struct")

            json_data = {
                'project': {
                    'project_name': 'Testing123'
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_project")

            json_data['project']['id_project'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_site")

            json_data['project']['id_site'] = 1
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to site")

            response = self._post_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Not site admin")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post OK")
            part_data = response.json[0]
            project_id = part_data['id_project']

            # Test update
            json_data = {
                'project': {
                    'id_project': project_id,
                    'id_site': 2,
                    'project_name': 'New Project Name'
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to site")

            del json_data['project']['id_site']
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Update completed")
            part_data = response.json[0]
            self.assertEqual(part_data['project_name'], 'New Project Name')

            json_data = {
                'project': {
                    'id_project': project_id,
                    'sessiontypes': [{'id_session_type': 1}, {'id_session_type': 6}]
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to at least one session type")

            st = TeraSessionType()
            st.from_json({'session_type_name': 'Test session type',
                          'session_type_online': False,
                          'session_type_color': '#000000',
                          'session_type_category': 2})
            TeraSessionType.insert(st)

            json_data = {
                'project': {
                    'id_project': project_id,
                    'sessiontypes': [{'id_session_type': 1}, {'id_session_type': st.id_session_type}]
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="At least one session type not associated to site")

            sts = TeraSessionTypeSite()
            sts.id_session_type = st.id_session_type
            sts.id_site = 1
            TeraSessionTypeSite.insert(sts)

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Update OK")

            # Test delete
            part1 = TeraParticipant()
            part1.from_json({'participant_name': 'Test Part #1',
                             'id_project': project_id})
            TeraParticipant.insert(part1)
            part2 = TeraParticipant()
            part2.from_json({'participant_name': 'Test Part #2',
                             'id_project': project_id})
            TeraParticipant.insert(part2)
            part2_session = TeraSession()
            part2_session.from_json({'id_session_type': 1,
                                     'session_name': 'Session #1',
                                     'session_start_datetime': datetime.datetime.now(),
                                     'session_status': 0,
                                     'id_creator_participant': part2.id_participant
                                     }
                                    )
            TeraSession.insert(part2_session)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': project_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has participants with sessions")

            TeraSession.delete(part2_session.id_session)
            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params={'id': project_id})
            self.assertEqual(403, response.status_code, msg="Can't delete, forbidden")

            id_part1 = part1.id_participant
            id_part2 = part2.id_participant
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': project_id})
            self.assertEqual(200, response.status_code, msg="Delete OK")

            # Check that all participants were also deleted
            self.assertEqual(TeraParticipant.get_participant_by_id(id_part1), None)
            self.assertEqual(TeraParticipant.get_participant_by_id(id_part2), None)

            # Check that all session type association were delete
            self.assertEqual(len(TeraSessionTypeProject.get_sessions_types_for_project(project_id)), 0)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_project'))
        self.assertTrue(json_data.__contains__('id_site'))
        self.assertTrue(json_data.__contains__('project_name'))

        if minimal:
            self.assertFalse(json_data.__contains__('site_name'))
            self.assertFalse(json_data.__contains__('project_role'))
            self.assertTrue(json_data.__contains__('project_participant_group_count'))
            self.assertTrue(json_data.__contains__('project_participant_count'))
        else:
            self.assertTrue(json_data.__contains__('site_name'))
            self.assertTrue(json_data.__contains__('project_role'))
            self.assertFalse(json_data.__contains__('project_participant_group_count'))
            self.assertFalse(json_data.__contains__('project_participant_count'))
