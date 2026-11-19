from tests.modules.FlaskModule.API.participant.BaseParticipantAPITest import BaseParticipantAPITest
from opentera.db.models.TeraParticipant import TeraParticipant


class ParticipantQueryParticipantsTest(BaseParticipantAPITest):
    login_endpoint = '/api/participant/login'
    test_endpoint = '/api/participant/participants'

    def setUp(self):
        super().setUp()
        with self._flask_app.app_context():
            participant = TeraParticipant.get_participant_by_username('participant1')
            self.participant_token = participant.participant_token

    def tearDown(self):
        super().tearDown()

    def test_query_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_query_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete(self):
        with self._flask_app.app_context():
            response = self._delete_with_participant_http_auth(self.test_client, username='participant1',
                                                               password='opentera', params={'id': 1})
            self.assertEqual(405, response.status_code)


    def test_query_http_auth_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera')
            self.assertEqual(200, response.status_code)

            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertGreater(len(response.json), 1)
            self._validate_json(response.json)
            participant = TeraParticipant.get_participant_by_username('participant1')
            self.assertEqual(response.json['id_participant'], participant.id_participant)

    def test_query_token_auth_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_token_auth(self.test_client, token=self.participant_token)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertGreater(len(response.json), 1)
            self._validate_json_token(response.json)
            participant = TeraParticipant.get_participant_by_username('participant1')
            self.assertEqual(response.json['participant_name'], participant.participant_name)

    def test_query_http_auth_invalid_params(self):
            params = {
                'invalid': 1
            }
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera', params=params)
            self.assertEqual(400, response.status_code)

    def test_query_http_auth_list_param(self):
        with self._flask_app.app_context():
            params = {
                'list': True
            }
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera', params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertGreater(len(response.json), 1)
            self._validate_json(response.json, True)
            participant = TeraParticipant.get_participant_by_username('participant1')
            self.assertEqual(response.json['id_participant'], participant.id_participant)

    def test_query_base_token(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_token_auth(self.test_client, token=self.participant_token)
            self.assertEqual(200, response.status_code)
            self._validate_json_token(response.json)
            participant = TeraParticipant.get_participant_by_username('participant1')
            self.assertEqual(response.json['participant_name'], participant.participant_name)

    def test_query_post_missing_participant(self):
        with self._flask_app.app_context():
            response = self._post_with_participant_token_auth(self.test_client, token=self.participant_token,
                                                              json = {'bad': []})
            self.assertEqual(400, response.status_code)

    def test_query_post_bad_format(self):
        with self._flask_app.app_context():
            response = self._post_with_participant_token_auth(self.test_client, token=self.participant_token,
                                                              json = {'participant': 'Bad'})
            self.assertEqual(400, response.status_code)

    def test_query_post_invalid_fields(self):
        with self._flask_app.app_context():
            response = self._post_with_participant_token_auth(self.test_client, token=self.participant_token,
                                                              json={'participant': {'participant_name': 'new_name',
                                                                                    'participant_email': 'x2@opentera.org',
                                                                                    'participant_enabled': True}})
            self.assertEqual(400, response.status_code)

    def test_query_post_invalid_name(self):
        with self._flask_app.app_context():
            response = self._post_with_participant_token_auth(self.test_client, token=self.participant_token,
                                                              json={'participant': {'participant_name': ''}})
            self.assertEqual(400, response.status_code)

    def test_query_post_invalid_email(self):
        with self._flask_app.app_context():
            response = self._post_with_participant_token_auth(self.test_client, token=self.participant_token,
                                                              json={'participant': {'participant_email': ''}})
            self.assertEqual(400, response.status_code)
            # Bad email format
            response = self._post_with_participant_token_auth(self.test_client, token=self.participant_token,
                                                              json={'participant': {'participant_email': 'x'}})
            self.assertEqual(400, response.status_code)

    def test_query_post_empty_participant(self):
        with self._flask_app.app_context():
            response = self._post_with_participant_token_auth(self.test_client, token=self.participant_token,
                                                              json={'participant': {}})
            self.assertEqual(400, response.status_code)

    def test_query_post_change_name_with_token(self):
        with self._flask_app.app_context():
            participant = TeraParticipant.get_participant_by_username('participant1')
            old_name = participant.participant_name
            response = self._post_with_participant_token_auth(self.test_client, token=self.participant_token,
                                                              json={'participant': {'participant_name': 'New name'}})
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            self._validate_json_token(response.json[0])
            self.assertEqual('New name', response.json[0]['participant_name'])
            participant = TeraParticipant.get_participant_by_username('participant1')
            self.assertEqual('New name', participant.participant_name)
            response = self._post_with_participant_token_auth(self.test_client, token=self.participant_token,
                                                              json={'participant': {'participant_name': old_name}})
            self.assertEqual(200, response.status_code)
            self.assertEqual(old_name, response.json[0]['participant_name'])

    def test_query_post_change_email_with_token(self):
        with self._flask_app.app_context():
            participant = TeraParticipant.get_participant_by_username('participant1')
            old_email = participant.participant_email
            response = self._post_with_participant_token_auth(self.test_client, token=self.participant_token,
                                                              json={'participant': {'participant_email': 'x@x.com'}})
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            self._validate_json_token(response.json[0])
            self.assertEqual('x@x.com', response.json[0]['participant_email'])
            participant = TeraParticipant.get_participant_by_username('participant1')
            self.assertEqual('x@x.com', participant.participant_email)
            response = self._post_with_participant_token_auth(self.test_client, token=self.participant_token,
                                                              json={'participant': {'participant_email': old_email}})
            self.assertEqual(200, response.status_code)
            self.assertEqual(old_email, response.json[0]['participant_email'])

    def test_query_post_change_name_with_http_auth(self):
        with self._flask_app.app_context():
            participant = TeraParticipant.get_participant_by_username('participant1')
            old_name = participant.participant_name
            response = self._post_with_participant_http_auth(self.test_client, username='participant1',
                                                             password='opentera',
                                                             json={'participant': {'participant_name': 'New name'}})
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            self._validate_json(response.json[0])
            self.assertEqual('New name', response.json[0]['participant_name'])
            participant = TeraParticipant.get_participant_by_username('participant1')
            self.assertEqual('New name', participant.participant_name)
            response = self._post_with_participant_http_auth(self.test_client, username='participant1',
                                                             password='opentera',
                                                             json={'participant': {'participant_name': old_name}})
            self.assertEqual(200, response.status_code)
            self.assertEqual(old_name, response.json[0]['participant_name'])

    def test_query_post_change_email_with_http_auth(self):
        with self._flask_app.app_context():
            participant = TeraParticipant.get_participant_by_username('participant1')
            old_email = participant.participant_email
            response = self._post_with_participant_http_auth(self.test_client, username='participant1',
                                                             password='opentera',
                                                              json={'participant': {'participant_email': 'x@x.com'}})
            self.assertEqual(200, response.status_code)
            self.assertEqual(len(response.json), 1)
            self._validate_json(response.json[0])
            self.assertEqual('x@x.com', response.json[0]['participant_email'])
            participant = TeraParticipant.get_participant_by_username('participant1')
            self.assertEqual('x@x.com', participant.participant_email)
            response = self._post_with_participant_http_auth(self.test_client, username='participant1',
                                                             password='opentera',
                                                             json={'participant': {'participant_email': old_email}})
            self.assertEqual(200, response.status_code)
            self.assertEqual(old_email, response.json[0]['participant_email'])

    def _validate_json(self, json, minimal=False):
        self.assertTrue(json.__contains__('id_participant'))
        self.assertTrue(json.__contains__('id_participant_group'))
        self.assertTrue(json.__contains__('id_project'))
        self.assertTrue(json.__contains__('participant_email'))
        self.assertTrue(json.__contains__('participant_enabled'))
        self.assertTrue(json.__contains__('participant_name'))
        self.assertFalse(json.__contains__('participant_password'))

    def _validate_json_token(self, json):
        self.assertTrue(json.__contains__('participant_name'))
        self.assertTrue(json.__contains__('participant_email'))
        self.assertFalse(json.__contains__('id_participant'))
        self.assertFalse(json.__contains__('id_participant_group'))
        self.assertFalse(json.__contains__('id_project'))
        self.assertFalse(json.__contains__('participant_password'))