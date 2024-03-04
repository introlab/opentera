from typing import List

from BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraProject import TeraProject


class ServiceQueryParticipantsTest(BaseServiceAPITest):
    test_endpoint = '/api/service/participants'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_with_wrong_params(self):
        with self._flask_app.app_context():
            # Get all participants from DB
            participants: List[TeraParticipant] = TeraParticipant.query.all()
            for participant in participants:
                params = {'participant_uuid_wrong': participant.participant_uuid}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_with_forbidden_uuid(self):
        with self._flask_app.app_context():
            # Get all participants from DB
            secret_participant = TeraParticipant.get_participant_by_name('Secret Participant')
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params={'participant_uuid':
                                                                 secret_participant.participant_uuid},
                                                         endpoint=self.test_endpoint)

            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_token_auth_with_participant_uuid(self):
        with self._flask_app.app_context():
            # Get all participants from DB
            participants: List[TeraParticipant] = TeraParticipant.query.all()
            for participant in participants:
                params = {'participant_uuid': participant.participant_uuid}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(200, response.status_code)
                participant_json = participant.to_json()
                self.assertEqual(participant_json, response.json)

    def test_get_endpoint_with_project_id(self):
        with self._flask_app.app_context():
            project_id = 1
            params = {'id_project': project_id}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            participants_count = TeraParticipant.get_count({'id_project': project_id})
            self.assertEqual(participants_count, len(response.json))

    def test_get_endpoint_with_forbidden_project_id(self):
        with self._flask_app.app_context():
            project_id = 2
            params = {'id_project': project_id}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_participant_group_id(self):
        with self._flask_app.app_context():
            group_id = 1
            params = {'id_participant_group': group_id}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            participants_count = TeraParticipant.get_count({'id_participant_group': group_id})
            self.assertEqual(participants_count, len(response.json))

    def test_get_endpoint_with_forbidden_participant_group_id(self):
        with self._flask_app.app_context():
            group_id = 2
            params = {'id_participant_group': group_id}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_search_by_name_in_project(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'name': '#1'}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))  # Only one participant has "#1" in their name

            params = {'id_project': 1, 'name': 'iciPAnt'}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            # Should return all participants in the project, since they all have that pattern in their name
            self.assertEqual(len(TeraParticipant.query_with_filters({'id_project': 1})), len(response.json))

    def test_get_endpoint_search_by_name_in_group(self):
        with self._flask_app.app_context():
            params = {'id_participant_group': 1, 'name': '#2'}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # No participant has "#1" in their name in that group

            params = {'id_participant_group': 1, 'name': 'ICipant'}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            # Should return all participants in the project, since they all have that pattern in their name
            self.assertEqual(len(TeraParticipant.query_with_filters({'id_participant_group': 1})), len(response.json))

    def test_get_endpoint_search_by_name_global(self):
        with self._flask_app.app_context():
            params = {'name': 'Secret'}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            # No participant available with that pattern (even if it exists)
            self.assertEqual(0, len(response.json))

            params = {'name': 'ICipant'}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            # Should return all participants, but only from the accessible project (1) for this service
            self.assertEqual(len(TeraParticipant.query_with_filters({'id_project': 1})), len(response.json))

    def test_post_endpoint_without_token_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint, json={})
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_with_token_auth_empty_json(self):
        with self._flask_app.app_context():
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token, json={},
                                                          endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_post_endpoint_with_token_auth_create_participant(self):
        with self._flask_app.app_context():
            participant_schema = {
                'participant': {
                    'id_participant': 0,
                    'id_project': 1,
                    'participant_name': 'test_participant',
                    'participant_email': 'test_participant_email'
                }
            }

            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=participant_schema, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            id_participant = response.json['id_participant']

            participant: TeraParticipant = TeraParticipant.get_participant_by_id(id_participant)
            self.assertEqual(response.json, participant.to_json(minimal=False))

    def test_post_endpoint_with_token_auth_update_participant(self):
        with self._flask_app.app_context():
            proj2: TeraProject = TeraProject.get_project_by_id(2)
            proj2.project_enabled = False
            proj2.db().session.commit()

            participant_schema = {
                'participant': {
                    'id_participant': 0,
                    'id_project': 2,
                    'participant_name': 'test_participant',
                    'participant_email': 'test_participant_email'
                }
            }

            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=participant_schema, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code, msg='Insert on a disabled project')
            proj2.project_enabled = True
            proj2.db().session.commit()

            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=participant_schema, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            id_participant = response.json['id_participant']

            participant: TeraParticipant = TeraParticipant.get_participant_by_id(id_participant)
            self.assertEqual(response.json, participant.to_json(minimal=False))
            # Store new id_participant
            participant_schema['participant']['id_participant'] = id_participant

            # Disable project and try to enable the participant
            proj2.project_enabled = False
            proj2.db().session.commit()
            participant_schema['participant']['participant_enabled'] = True
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=participant_schema, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code, msg='Cant enable on disabled project')
            del participant_schema['participant']['participant_enabled']

            # Update name, even if disabled, should be OK!
            participant_schema['participant']['participant_name'] = 'updated test_participant'
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=participant_schema, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            proj2.project_enabled = True
            proj2.db().session.commit()
            participant = TeraParticipant.get_participant_by_id(id_participant)
            self.assertEqual(response.json['id_participant'], participant.id_participant)
            self.assertEqual(participant_schema['participant']['participant_name'], response.json['participant_name'])
            self.assertEqual(participant_schema['participant']['participant_name'], participant.participant_name)

            # Update email
            participant_schema['participant']['participant_email'] = 'updated test_participant_email'
            response = self._post_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                          json=participant_schema, endpoint=self.test_endpoint)
            self.assertEqual(200, response.status_code)
            participant = TeraParticipant.get_participant_by_id(id_participant)
            self.assertEqual(response.json['id_participant'], participant.id_participant)
            self.assertEqual(participant_schema['participant']['participant_email'], response.json['participant_email'])
            self.assertEqual(participant_schema['participant']['participant_email'], participant.participant_email)
