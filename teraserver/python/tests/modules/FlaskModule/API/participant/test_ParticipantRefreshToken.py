from tests.modules.FlaskModule.API.participant.BaseParticipantAPITest import BaseParticipantAPITest


class ParticipantRefreshTokenTest(BaseParticipantAPITest):
    test_endpoint = '/api/participant/refresh_token'
    login_endpoint = '/api/participant/login'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_valid_refresh_token(self):
        with self._flask_app.app_context():
            # Get the token from http auth
            httpauth_response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                                     password='opentera', endpoint=self.login_endpoint)
            self.assertEqual(200, httpauth_response.status_code)
            self.assertEqual('application/json', httpauth_response.headers['Content-Type'])

            self.assertGreater(len(httpauth_response.json), 0)
            self.assertTrue('participant_token' in httpauth_response.json)
            login_token = httpauth_response.json['participant_token']
            self.assertGreater(len(login_token), 0)

            # Try to refresh token
            response = self._get_with_participant_token_auth(self.test_client, token=login_token)
            self.assertEqual(200, response.status_code)
            self.assertTrue('refresh_token' in response.json)
            self.assertGreater(len(response.json['refresh_token']), 0)

    def test_invalid_refresh_token(self):
        with self._flask_app.app_context():
            # Try to refresh token
            response = self._get_with_participant_token_auth(self.test_client, token='')
            self.assertEqual(401, response.status_code)

    def test_invalid_refresh_token_from_disabled_token(self):
        with self._flask_app.app_context():
            # Get the token from http auth
            httpauth_response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                                     password='opentera', endpoint=self.login_endpoint)
            self.assertEqual(200, httpauth_response.status_code)
            self.assertEqual('application/json', httpauth_response.headers['Content-Type'])

            self.assertGreater(len(httpauth_response.json), 0)
            self.assertTrue('participant_token' in httpauth_response.json)
            login_token = httpauth_response.json['participant_token']
            self.assertGreater(len(login_token), 0)

            # Try to refresh token, should work
            response = self._get_with_participant_token_auth(self.test_client, token=login_token)
            self.assertEqual(200, response.status_code)
            self.assertTrue('refresh_token' in response.json)
            self.assertGreater(len(response.json['refresh_token']), 0)

            # Try to refresh same login token, should not work because it is disabled
            response = self._get_with_participant_token_auth(self.test_client, token=login_token)
            self.assertEqual(401, response.status_code)
