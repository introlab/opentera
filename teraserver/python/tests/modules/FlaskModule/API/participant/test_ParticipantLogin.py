from BaseParticipantAPITest import BaseParticipantAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraParticipant import TeraParticipant


class ParticipantLoginTest(BaseParticipantAPITest):
    test_endpoint = '/api/participant/login'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(response.status_code, 401)

    def test_get_endpoint_login_valid_participant_http_auth(self):
        with self._flask_app.app_context():
            # Using default participant information
            response = self._get_with_participant_http_auth(self.test_client, 'participant1', 'opentera')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertGreater(len(response.json), 0)

            # Validate fields in json response
            self.assertTrue('websocket_url' in response.json)
            self.assertTrue('participant_uuid' in response.json)
            self.assertTrue('participant_token' in response.json)
            self.assertTrue('base_token' in response.json)
            self.assertGreater(len(response.json['websocket_url']), 0)
            self.assertGreater(len(response.json['participant_uuid']), 0)
            self.assertGreater(len(response.json['participant_token']), 0)
            self.assertGreater(len(response.json['base_token']), 0)

    def test_get_endpoint_login_invalid_participant_httpauth(self):
        with self._flask_app.app_context():
            # Using default participant information
            response = self._get_with_participant_http_auth(self.test_client, 'invalid', 'invalid')
            self.assertEqual(response.status_code, 401)

    def test_get_endpoint_login_valid_token_auth(self):
        with self._flask_app.app_context():
            for participant in TeraParticipant.query.all():
                if participant.participant_token is None:
                    continue

                response = self._get_with_participant_token_auth(self.test_client, token=participant.participant_token)
                if not participant.participant_enabled:
                    self.assertEqual(response.status_code, 401)
                    continue

                self.assertEqual(response.status_code, 200)
                self.assertTrue('websocket_url' in response.json)
                self.assertTrue('participant_uuid' in response.json)
                self.assertTrue('participant_name' in response.json)
                self.assertTrue('base_token' in response.json)
                self.assertGreater(len(response.json['websocket_url']), 0)
                self.assertGreater(len(response.json['participant_uuid']), 0)
                self.assertGreater(len(response.json['participant_name']), 0)
                self.assertGreater(len(response.json['base_token']), 0)

    def test_get_endpoint_login_base_token_auth(self):
        # Get the token from http auth
        with self._flask_app.app_context():
            # Using default participant information
            response = self._get_with_participant_http_auth(self.test_client, 'participant1', 'opentera')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertGreater(len(response.json), 0)
            self.assertTrue('base_token' in response.json)
            base_token = response.json['base_token']
            self.assertGreater(len(base_token), 0)

            # Now try to login with token
            response = self._get_with_participant_token_auth(self.test_client, token=base_token)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertGreater(len(response.json), 0)
            self.assertTrue('base_token' in response.json)
            self.assertFalse('participant_token' in response.json)  # participant_token not there, since token login
            self.assertGreater(len(response.json['base_token']), 0)
