from BaseParticipantAPITest import BaseParticipantAPITest
from opentera.db.models.TeraParticipant import TeraParticipant


class ParticipantLogoutTest(BaseParticipantAPITest):

    test_endpoint = '/api/participant/logout'
    login_endpoint = '/api/participant/login'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_logout_valid_participant_httpauth(self):
        with self._flask_app.app_context():
            # Using default participant information
            username = 'participant1'
            password = 'opentera'

            login_response = self._get_with_participant_http_auth(
                self.test_client, username, password, params={}, endpoint=self.login_endpoint)

            self.assertEqual(200, login_response.status_code)
            self.assertEqual('application/json', login_response.headers['Content-Type'])
            self.assertGreater(len(login_response.json), 0)

            logout_response = self._get_with_participant_http_auth(
                self.test_client, username, password, params={}, endpoint=self.test_endpoint)

            self.assertEqual('application/json', logout_response.headers['Content-Type'])
            self.assertEqual(200, logout_response.status_code)

    def test_logout_invalid_participant_httpauth(self):
        with self._flask_app.app_context():
            username = 'invalid'
            password = 'invalid'

            login_response = self._get_with_participant_http_auth(
                self.test_client, username, password, params={}, endpoint=self.login_endpoint)

            self.assertEqual(401, login_response.status_code)

            logout_response = self._get_with_participant_http_auth(
                self.test_client, username, password, params={}, endpoint=self.test_endpoint)

            self.assertEqual(401, logout_response.status_code)

    def test_logout_valid_token_auth(self):
        with self._flask_app.app_context():

            for participant in TeraParticipant.query.all():
                if participant.participant_token is None:
                    continue

                login_response = self._get_with_participant_token_auth(
                    self.test_client, token=participant.participant_token, endpoint=self.login_endpoint)
                if not participant.participant_enabled:
                    self.assertEqual(401, login_response.status_code)
                    continue

                self.assertEqual(200, login_response.status_code)

                logout_response = self._get_with_participant_token_auth(
                    self.test_client, token=participant.participant_token, endpoint=self.test_endpoint)

                self.assertEqual('application/json', logout_response.headers['Content-Type'])
                self.assertEqual(200, logout_response.status_code)
