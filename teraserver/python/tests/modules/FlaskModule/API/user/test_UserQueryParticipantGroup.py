from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSession import TeraSession
import datetime


class UserQueryParticipantGroupTest(BaseUserAPITest):
    test_endpoint = '/api/user/groups'

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

    def test_query_specific_group_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params='id_group=1')
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=False)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params='id_group=1&list=1')
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=True)

    def test_query_specific_group_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params='id_group=1')
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params='id_group=1')
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=False)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params='id_group=1&list=1')
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=True)

    def test_query_for_project_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params='id_project=1')
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = len(TeraParticipantGroup.get_participant_group_for_project(1))
            self.assertEqual(len(json_data), target_count)
            for group_data in json_data:
                self._checkJson(json_data=group_data, minimal=False)

    def test_query_for_project_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params='id_project=1')
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params='id_project=1')
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = len(TeraParticipantGroup.get_participant_group_for_project(1))
            self.assertEqual(len(json_data), target_count)
            for group_data in json_data:
                self._checkJson(json_data=group_data, minimal=False)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                'participant_group_name': 'Testing123',
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing group struct")

            json_data = {
                'participant_group': {
                    'participant_group_name': 'Testing123'
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing id_participant_group")

            json_data['participant_group']['id_participant_group'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing id_project")

            json_data['participant_group']['id_project'] = 1
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(response.status_code, 403, msg="No access to project")

            response = self._post_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

            part_data = response.json[0]
            self._checkJson(part_data)
            group_id = part_data['id_participant_group']

            # Test update
            json_data = {
                'participant_group': {
                    'id_participant_group': group_id,
                    'id_project': 3
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                      json=json_data)
            self.assertEqual(response.status_code, 403, msg="No access to new project")

            json_data['participant_group']['id_project'] = 2
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(response.status_code, 403, msg="No access to group")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Update completed")
            part_data = response.json[0]
            self._checkJson(part_data)
            self.assertEqual(part_data['id_project'], 2)

            # Test delete
            part1 = TeraParticipant()
            part1.from_json({'participant_name': 'Test Part #1',
                             'id_participant_group': group_id,
                             'id_project': 2})
            TeraParticipant.insert(part1)
            part2 = TeraParticipant()
            part2.from_json({'participant_name': 'Test Part #2',
                             'id_participant_group': group_id,
                             'id_project': 2})
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
                                                        params={'id': group_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has participants with sessions")

            TeraSession.delete(part2_session.id_session)
            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params={'id': group_id})
            self.assertEqual(response.status_code, 403, msg="Can't delete, forbidden")

            id_part1 = part1.id_participant
            id_part2 = part2.id_participant
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': group_id})
            self.assertEqual(response.status_code, 200, msg="Delete OK")

            # Check that all participants were also deleted
            self.assertEqual(TeraParticipant.get_participant_by_id(id_part1), None)
            self.assertEqual(TeraParticipant.get_participant_by_id(id_part2), None)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_participant_group'))
        self.assertTrue(json_data.__contains__('id_project'))
        self.assertTrue(json_data.__contains__('participant_group_name'))

        if minimal:
            self.assertTrue(json_data.__contains__('group_participant_count'))
            self.assertFalse(json_data.__contains__('project_name'))
        else:
            self.assertFalse(json_data.__contains__('group_participant_count'))
            self.assertTrue(json_data.__contains__('project_name'))
