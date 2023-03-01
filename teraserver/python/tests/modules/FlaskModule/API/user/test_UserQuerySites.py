from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSession import TeraSession
import datetime


class UserQuerySitesTest(BaseUserAPITest):
    test_endpoint = '/api/user/sites'

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

    def test_query_specific_site_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self._checkJson(json_data=response.json[0], minimal=False)
            id_site = response.json[0]['id_site']
            name = response.json[0]['site_name']

            # by name
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'name': name})
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))
            self._checkJson(json_data=response.json[0], minimal=False)
            self.assertEqual(response.json[0]['id_site'], id_site)

    def test_query_specific_site_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.json, [])

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            self._checkJson(json_data=response.json[0], minimal=False)
            id_site = response.json[0]['id_site']
            name = response.json[0]['site_name']

            # by name
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'name': name})
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            self._checkJson(json_data=response.json[0], minimal=False)
            self.assertEqual(response.json[0]['id_site'], id_site)

    def test_query_specific_user_uuid(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('admin')
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'user_uuid': user.user_uuid})
            self.assertEqual(200, response.status_code)
            target_count = len(user.get_sites_roles())
            self.assertEqual(target_count, len(response.json))
            for part_data in response.json:
                self._checkJson(json_data=part_data, minimal=False)

            user = TeraUser.get_user_by_username('user3')
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'user_uuid': user.user_uuid})
            self.assertEqual(200, response.status_code)
            target_count = len(user.get_sites_roles())
            self.assertEqual(target_count, len(response.json))
            for part_data in response.json:
                self._checkJson(json_data=part_data, minimal=False)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                'site_name': 'Testing123',
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing site struct")

            json_data = {
                'site': {
                    'site_name': 'Testing123'
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_site")

            json_data['site']['id_site'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No access to create site")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Not super admin")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post OK")
            part_data = response.json[0]
            site_id = part_data['id_site']

            # Test update
            json_data = {
                'site': {
                    'id_site': site_id,
                    'site_name': 'New Site Name'
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="No super admin access")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Update completed")
            part_data = response.json[0]
            self.assertEqual(part_data['site_name'], 'New Site Name')

            # Test delete
            site_project = TeraProject()
            site_project.id_site = site_id
            site_project.project_name = 'Site Project'
            TeraProject.insert(site_project)

            part1 = TeraParticipant()
            part1.from_json({'participant_name': 'Test Part #1',
                             'id_project': site_project.id_project})
            TeraParticipant.insert(part1)
            part2 = TeraParticipant()
            part2.from_json({'participant_name': 'Test Part #2',
                             'id_project': site_project.id_project})
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
                                                        params={'id': site_id})
            self.assertEqual(500, response.status_code, msg="Can't delete, has participants with sessions")

            TeraSession.delete(part2_session.id_session)
            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params={'id': site_id})
            self.assertEqual(403, response.status_code, msg="Can't delete, forbidden")

            id_part1 = part1.id_participant
            id_part2 = part2.id_participant
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': site_id})
            self.assertEqual(200, response.status_code, msg="Delete OK")

            # Check that all participants were also deleted
            self.assertEqual(None, TeraParticipant.get_participant_by_id(id_part1))
            self.assertEqual(None, TeraParticipant.get_participant_by_id(id_part2))

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_site'))
        self.assertTrue(json_data.__contains__('site_name'))
        self.assertTrue(json_data.__contains__('site_role'))
