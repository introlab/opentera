from BaseParticipantAPITest import BaseParticipantAPITest


class ParticipantQueryParticipantsTest(BaseParticipantAPITest):
    login_endpoint = '/api/participant/login'
    test_endpoint = '/api/participant/participants'

    def setUp(self):
        super().setUp()

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

    def test_query_http_auth_no_params(self):
        response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                        password='opentera')
        self.assertEqual(200, response.status_code)

        self.assertEqual('application/json', response.headers['Content-Type'])
        self.assertGreater(len(response.json), 0)
        self.assertTrue(response.json.__contains__('id_participant'))
        self.assertTrue(response.json.__contains__('id_participant_group'))
        self.assertTrue(response.json.__contains__('id_project'))
        self.assertTrue(response.json.__contains__('participant_email'))
        self.assertTrue(response.json.__contains__('participant_enabled'))
        self.assertTrue(response.json.__contains__('participant_name'))
        self.assertFalse(response.json.__contains__('participant_password'))

    def test_query_token_auth_no_params(self):
        # HTTP AUTH REQUIRED TO GET TOKEN
        response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                        password='opentera', endpoint=self.login_endpoint)
        self.assertEqual(200, response.status_code)
        self.assertTrue('participant_token' in response.json)
        token = response.json['participant_token']

        response = self._get_with_participant_token_auth(self.test_client, token=token)
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response.headers['Content-Type'])
        self.assertGreater(len(response.json), 0)
        self.assertTrue(response.json.__contains__('id_participant'))
        self.assertTrue(response.json.__contains__('id_participant_group'))
        self.assertTrue(response.json.__contains__('id_project'))
        self.assertTrue(response.json.__contains__('participant_email'))
        self.assertTrue(response.json.__contains__('participant_enabled'))
        self.assertTrue(response.json.__contains__('participant_name'))
        self.assertFalse(response.json.__contains__('participant_password'))

    def test_query_http_auth_invalid_params(self):
        params = {
            'invalid': 1
        }
        response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                        password='opentera', params=params)
        self.assertEqual(400, response.status_code)

    def test_query_http_auth_list_param(self):
        params = {
            'list': True
        }
        response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                        password='opentera', params=params)
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/json', response.headers['Content-Type'])
        self.assertGreater(len(response.json), 0)

    def test_query_base_token(self):
        # HTTP AUTH REQUIRED TO GET TOKEN
        response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                        password='opentera', endpoint=self.login_endpoint)
        self.assertEqual(200, response.status_code)
        self.assertTrue('base_token' in response.json)
        token = response.json['base_token']

        response = self._get_with_participant_token_auth(self.test_client, token=token)
        # Now allowed to get participant information with token
        self.assertEqual(200, response.status_code)
