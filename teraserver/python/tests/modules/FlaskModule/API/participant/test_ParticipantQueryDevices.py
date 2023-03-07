from BaseParticipantAPITest import BaseParticipantAPITest


class ParticipantQueryDevicesTest(BaseParticipantAPITest):
    login_endpoint = '/api/participant/login'
    test_endpoint = '/api/participant/devices'

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
        with self._flask_app.app_context():
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera')
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertGreater(len(response.json), 0)

            for data_item in response.json:
                self.assertGreater(len(data_item), 0)
                self.assertTrue(data_item.__contains__('device_config'))
                self.assertTrue(data_item.__contains__('device_enabled'))
                self.assertTrue(data_item.__contains__('device_lastonline'))
                self.assertTrue(data_item.__contains__('device_name'))
                self.assertTrue(data_item.__contains__('device_notes'))
                self.assertTrue(data_item.__contains__('device_onlineable'))
                self.assertTrue(data_item.__contains__('id_device_type'))
                self.assertTrue(data_item.__contains__('id_device_subtype'))
                self.assertTrue(data_item.__contains__('device_uuid'))
                self.assertTrue(data_item.__contains__('id_device'))

    def test_query_token_auth_no_params(self):
        with self._flask_app.app_context():
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

            for data_item in response.json:
                self.assertGreater(len(data_item), 0)
                self.assertTrue(data_item.__contains__('device_config'))
                self.assertTrue(data_item.__contains__('device_enabled'))
                self.assertTrue(data_item.__contains__('device_lastonline'))
                self.assertTrue(data_item.__contains__('device_name'))
                self.assertTrue(data_item.__contains__('device_notes'))
                self.assertTrue(data_item.__contains__('device_onlineable'))
                self.assertTrue(data_item.__contains__('id_device_type'))
                self.assertTrue(data_item.__contains__('id_device_subtype'))
                self.assertTrue(data_item.__contains__('device_uuid'))
                self.assertTrue(data_item.__contains__('id_device'))

    def test_query_base_token(self):
        with self._flask_app.app_context():
            # HTTP AUTH REQUIRED TO GET TOKEN
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera', endpoint=self.login_endpoint)
            self.assertEqual(200, response.status_code)
            self.assertTrue('base_token' in response.json)
            token = response.json['base_token']

            response = self._get_with_participant_token_auth(self.test_client, token=token)
            # Should not be allowed
            self.assertEqual(403, response.status_code)
