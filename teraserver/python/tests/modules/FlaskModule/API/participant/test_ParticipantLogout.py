from BaseParticipantAPITest import BaseParticipantAPITest
from opentera.db.models.TeraParticipant import TeraParticipant


class ParticipantLogoutTest(BaseParticipantAPITest):

    test_endpoint = '/api/participant/logout'

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
                self.test_client, username, password, params={}, endpoint='/api/participant/login')

            self.assertEqual(login_response.status_code, 200)
            self.assertEqual(login_response.headers['Content-Type'], 'application/json')
            self.assertGreater(len(login_response.json), 0)

            logout_response = self._get_with_participant_http_auth(
                self.test_client, username, password, params={}, endpoint=self.test_endpoint)

            self.assertEqual(logout_response.headers['Content-Type'], 'application/json')
            self.assertEqual(logout_response.status_code, 200)

    def test_logout_invalid_participant_httpauth(self):
        with self._flask_app.app_context():
            username = 'invalid'
            password = 'invalid'

            login_response = self._get_with_participant_http_auth(
                self.test_client, username, password, params={}, endpoint='/api/participant/login')

            self.assertEqual(login_response.status_code, 401)

            logout_response = self._get_with_participant_http_auth(
                self.test_client, username, password, params={}, endpoint=self.test_endpoint)

            self.assertEqual(logout_response.status_code, 401)

    def test_logout_valid_token_auth(self):
        with self._flask_app.app_context():

            for participant in TeraParticipant.query.all():
                if participant.participant_token is None:
                    continue

                login_response = self._get_with_participant_token_auth(
                    self.test_client, token=participant.participant_token, endpoint='/api/participant/login')
                if not participant.participant_enabled:
                    self.assertEqual(login_response.status_code, 401)
                    continue

                self.assertEqual(login_response.status_code, 200)

                logout_response = self._get_with_participant_token_auth(
                    self.test_client, token=participant.participant_token, endpoint=self.test_endpoint)

                self.assertEqual(logout_response.headers['Content-Type'], 'application/json')
                self.assertEqual(logout_response.status_code, 200)
