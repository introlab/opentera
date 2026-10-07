from opentera.db.models import TeraSite
from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraService import TeraService

import datetime


class UserQueryParticipantsTest(BaseUserAPITest):
    test_endpoint = '/api/user/participants'

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

    def test_query_no_params_as_admin(self):
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
        self.assertEqual(response.status_code, 400)

    def test_query_specific_participant_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_participant': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=False)
            id_participant = json_data[0]['id_participant']
            uuid_participant = json_data[0]['participant_uuid']
            username = json_data[0]['participant_username']

            # by uuid
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'participant_uuid': uuid_participant})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=False)
            self.assertEqual(json_data[0]['id_participant'], id_participant)

            # by username
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'username': username})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=False)
            self.assertEqual(json_data[0]['id_participant'], id_participant)

            # with minimal infos
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_participant': 1, 'list': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=True)

    def test_query_specific_participant_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_participant': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'id_participant': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=False)
            id_participant = json_data[0]['id_participant']
            uuid_participant = json_data[0]['participant_uuid']
            username = json_data[0]['participant_username']

            # by uuid
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'participant_uuid': uuid_participant})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=False)
            self.assertEqual(json_data[0]['id_participant'], id_participant)

            # by username
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'username': username})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=False)
            self.assertEqual(json_data[0]['id_participant'], id_participant)

            # with minimal infos
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'id_participant': 1, 'list': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=True)

    def test_query_specific_site(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_site': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = TeraParticipant.query.join(TeraProject).filter(TeraProject.id_site == 1).count()
            self.assertEqual(target_count, len(json_data))
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

            # Only with enabled
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1, 'enabled': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = TeraParticipant.query.join(TeraProject).filter(TeraProject.id_site == 1,
                                                                          TeraParticipant.participant_enabled == True) \
                .count()
            self.assertEqual(target_count, len(json_data))
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_specific_project(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_project': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = TeraParticipant.query.join(TeraProject).filter(TeraProject.id_project == 1).count()
            self.assertEqual(target_count, len(json_data))
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

            # Only with enabled
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1, 'enabled': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = TeraParticipant.query.join(TeraProject).filter(TeraProject.id_project == 1,
                                                                          TeraParticipant.participant_enabled == True) \
                .count()
            self.assertEqual(target_count, len(json_data))
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_specific_participant_group(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_group': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_group': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = len(TeraParticipantGroup.get_participant_group_by_id(1).participant_group_participants)
            self.assertEqual(len(json_data), target_count)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_specific_session(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_session': 2})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_session': 2})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = TeraSessionParticipants.get_count(filters={'id_session': 2})
            self.assertEqual(len(json_data), target_count)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_specific_device(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params={'id_device': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_device': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = len(TeraDeviceParticipant.query_participants_for_device(1))
            self.assertEqual(len(json_data), target_count)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_full_infos(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_participant': 1, 'full': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0], minimal=False)
            self.assertTrue(json_data[0].__contains__('participant_participant_group'))
            self.assertTrue(json_data[0].__contains__('participant_project'))
            self.assertTrue(json_data[0].__contains__('participant_devices'))

    def test_query_recents(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1, 'orderby_recents': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            participants = TeraParticipant.query.join(TeraProject).filter(TeraProject.id_site == 1).all()
            participants = sorted(participants, key=lambda sort_part: sort_part.version_id, reverse=True)
            self.assertEqual(len(json_data), len(participants))
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)
            for i in range(len(json_data)):
                self.assertEqual(participants[i].id_participant, json_data[i]['id_participant'])

    def test_query_limit_for_site(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1, 'limit': 2})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 2)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_offset_for_site(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1, 'offset': 2})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_site = TeraSite.get_site_by_id(1)
            target_projects = target_site.site_projects
            target_count = sum([len(proj.project_participants) for proj in target_projects])
            self.assertEqual(len(json_data), target_count - 2)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_limit_and_offset_for_site(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1, 'offset': 1, 'limit': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_site = TeraSite.get_site_by_id(1)
            target_projects = target_site.site_projects
            self.assertEqual(len(json_data), 1)
            self.assertEqual(json_data[0]['id_participant'], target_projects[0].project_participants[1].id_participant)

            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_limit_for_project(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1, 'limit': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_offset_for_project(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1, 'offset': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_project = TeraProject.get_project_by_id(1)
            target_count = len(target_project.project_participants)
            self.assertEqual(len(json_data), target_count - 1)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_limit_and_offset_for_project(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1, 'offset': 1, 'limit': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_project = TeraProject.get_project_by_id(1)
            self.assertEqual(len(json_data), 1)
            self.assertEqual(json_data[0]['id_participant'], target_project.project_participants[1].id_participant)

            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_limit_for_group(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_group': 1, 'limit': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_offset_for_group(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_group': 1, 'offset': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            # target_group = TeraParticipantGroup.get_participant_group_by_id(1)
            # target_count = len(target_group.participant_group_project.project_participants)
            # self.assertEqual(len(json_data), target_count - 1)
            self.assertEqual(len(json_data), 0)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_limit_and_offset_for_group(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_group': 1, 'offset': 0, 'limit': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_group = TeraParticipantGroup.get_participant_group_by_id(1)
            self.assertEqual(len(json_data), 1)
            self.assertEqual(json_data[0]['id_participant'],
                             target_group.participant_group_project.project_participants[0].id_participant)

            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_limit_for_device(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_device': 1, 'limit': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_offset_for_device(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_device': 1, 'offset': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_participants = TeraDeviceParticipant.query_participants_for_device(1)
            target_count = len(target_participants)
            self.assertEqual(len(json_data), target_count - 1)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_limit_and_offset_for_device(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_device': 1, 'offset': 1, 'limit': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_participants = TeraDeviceParticipant.query_participants_for_device(1)
            self.assertEqual(len(json_data), 1)
            self.assertEqual(json_data[0]['id_participant'],
                             target_participants[1].id_participant)

            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_no_group(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1, 'no_group': 1})
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = TeraParticipant.get_count(filters={'id_participant_group': None, 'id_project': 1})
            self.assertEqual(len(json_data), target_count)
            for part_data in json_data:
                self._checkJson(json_data=part_data, minimal=False)

    def test_query_search_wrong_type(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'search': 'bad', 'search_value': 'error'})
            self.assertEqual(response.status_code, 400)

    def test_query_search_missing_value(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'search': 'all'})
            self.assertEqual(response.status_code, 400)

    def test_query_search_name(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'search': 'name', 'search_value': "missing"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'search': 'name', 'search_value': " #"})
            self.assertEqual(response.status_code, 200)
            target_count = len(TeraParticipant.search_participant_by_name(' #'))
            self.assertEqual(len(response.json), target_count)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'search': 'name', 'search_value': "Participant"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), target_count)  # Should have the same count (no "Secret Participant")

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'search': 'name', 'search_value': "participant"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), target_count)  # Validate case insensitivity

    def test_query_search_email(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'search': 'email', 'search_value': " #"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'search': 'email', 'search_value': "opentera"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)

    def test_query_search_username(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'search': 'username', 'search_value': "opentera"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'search': 'username', 'search_value': "particip"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)

    def test_query_search_all(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'search': 'all', 'search_value': "none"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'search': 'all', 'search_value': " #"})
            self.assertEqual(response.status_code, 200)
            target_count = len(TeraParticipant.search_participant_by_name(' #'))
            self.assertEqual(len(response.json), target_count)

            response = self._get_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                     params={'search': 'all', 'search_value': "@"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'search': 'all', 'search_value': "particip"})
            self.assertEqual(response.status_code, 200)
            target_count = len(TeraParticipant.search_participant_by_name('particip'))
            self.assertEqual(len(response.json), target_count)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
            json_data = {
                    'participant_name': 'Testing123',
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing participant struct")

            json_data = {
                'participant': {
                    'participant_name': 'Testing123',
                }
            }

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing id_user & id_project")

            json_data['participant']['id_participant'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing id_project or participant group")

            json_data['participant']['id_project'] = 1
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(response.status_code, 403, msg="No access to project")

            response = self._post_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

            part_data = response.json[0]
            self._checkJson(part_data)
            first_new_id = part_data['id_participant']

            # Try to create with participant group
            del json_data['participant']['id_project']
            json_data['participant']['id_participant_group'] = 1
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(response.status_code, 403, msg="No access to participant group")

            json_data['participant']['id_project'] = 2
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Mismatch between project and group")

            del json_data['participant']['id_participant_group']
            proj2: TeraProject = TeraProject.get_project_by_id(2)
            proj2.project_enabled = False
            proj2.db().session.commit()

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Project disabled")  # All ok now!

            proj2.project_enabled = True
            proj2.db().session.commit()

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!
            part_data = response.json[0]
            self._checkJson(part_data)
            second_new_id = part_data['id_participant']

            # Test update
            json_data = {
                'participant': {
                    'id_participant': second_new_id,
                    'participant_enabled': True,
                    'id_participant_group': 5
                }
            }
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 403, msg="Participant group not found")

            del json_data['participant']['id_participant_group']
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(response.status_code, 403, msg="Update forbidden")

            proj2.project_enabled = False
            proj2.db().session.commit()
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="No update - project disabled")

            json_data['participant']['participant_enabled'] = False
            json_data['participant']['participant_name'] = 'TestingNameChange'
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Update other than enabled = OK")
            part_data = response.json[0]
            self.assertEqual(part_data['participant_name'], 'TestingNameChange')
            self.assertEqual(part_data['participant_enabled'], False)

            proj2.project_enabled = True
            proj2.db().session.commit()

            json_data['participant']['participant_enabled'] = True
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 200, msg="Update completed")
            part_data = response.json[0]
            self._checkJson(part_data)
            self.assertEqual(part_data['participant_enabled'], True)

            # Delete newly created participant
            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params={'id': second_new_id})
            self.assertEqual(response.status_code, 403, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': second_new_id})
            self.assertEqual(response.status_code, 200, msg="Delete OK")

            # Create session, test and asset for a participant and try to delete
            json_session = {'id_session_type': 1,
                            'session_name': 'Session #1',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0
                            }
            new_session = TeraSession()
            new_session.from_json(json_session)
            TeraSession.insert(new_session)
            session1 = new_session
            json_part_session = {'id_session': session1.id_session,
                                 'id_participant': first_new_id
                                 }
            new_part_session = TeraSessionParticipants()
            new_part_session.from_json(json_part_session)
            TeraSessionParticipants.insert(new_part_session)
            json_session = {'id_session_type': 1,
                            'session_name': 'Session #2',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            'id_creator_participant': first_new_id
                            }
            new_session = TeraSession()
            new_session.from_json(json_session)
            TeraSession.insert(new_session)
            session2 = new_session
            json_session = {'id_session_type': 1,
                            'session_name': 'Session #3',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            }
            new_session = TeraSession()
            new_session.from_json(json_session)
            TeraSession.insert(new_session)
            session3 = new_session
            json_session = {'id_session_type': 1,
                            'session_name': 'Session #4',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            }
            new_session = TeraSession()
            new_session.from_json(json_session)
            TeraSession.insert(new_session)
            session4 = new_session
            json_test = {'id_test_type': 1,
                         'id_session': session3.id_session,
                         'test_name': 'Test Participant',
                         'id_participant': first_new_id,
                         'test_datetime': datetime.datetime.now()
                         }
            new_test = TeraTest()
            new_test.from_json(json_test)
            TeraTest.insert(new_test)
            service_uuid = TeraService.get_openteraserver_service().service_uuid
            json_asset = {'id_session': session4.id_session,
                          'id_participant': first_new_id,
                          'asset_name': 'Test Participant Asset',
                          'asset_type': 'Test asset',
                          'asset_service_uuid': service_uuid}
            new_asset = TeraAsset()
            new_asset.from_json(json_asset)
            TeraAsset.insert(new_asset)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': first_new_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has sessions")

            TeraSession.delete(session1.id_session)
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': first_new_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has created sessions")

            TeraSession.delete(session2.id_session)
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': first_new_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has assets")
            TeraAsset.delete(new_asset.id_asset)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': first_new_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has tests")
            TeraTest.delete(new_test.id_test)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': first_new_id})
            self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_participant'))
        self.assertTrue(json_data.__contains__('id_participant_group'))
        self.assertTrue(json_data.__contains__('participant_uuid'))
        self.assertTrue(json_data.__contains__('participant_name'))
        self.assertTrue(json_data.__contains__('participant_email'))
        self.assertTrue(json_data.__contains__('participant_token_enabled'))
        self.assertTrue(json_data.__contains__('participant_enabled'))
        self.assertFalse(json_data.__contains__('participant_password'))

        if minimal:
            self.assertFalse(json_data.__contains__('participant_username'))
            self.assertFalse(json_data.__contains__('participant_token'))
            self.assertFalse(json_data.__contains__('participant_lastonline'))
            self.assertFalse(json_data.__contains__('participant_login_enabled'))
            self.assertFalse(json_data.__contains__('participant_project_enabled'))
        else:
            self.assertTrue(json_data.__contains__('participant_username'))
            self.assertTrue(json_data.__contains__('participant_token'))
            self.assertTrue(json_data.__contains__('participant_lastonline'))
            self.assertTrue(json_data.__contains__('participant_login_enabled'))
            self.assertTrue(json_data.__contains__('participant_project_enabled'))
