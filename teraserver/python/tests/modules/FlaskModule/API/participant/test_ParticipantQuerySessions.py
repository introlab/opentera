from datetime import datetime, timedelta
from BaseParticipantAPITest import BaseParticipantAPITest


class ParticipantQuerySessionsTest(BaseParticipantAPITest):
    test_endpoint = '/api/participant/sessions'
    login_endpoint = '/api/participant/login'

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
                if data_item['id_creator_device']:
                    self.assertTrue(data_item.__contains__('session_creator_device'))

                self.assertTrue(data_item.__contains__('id_creator_participant'))
                if data_item['id_creator_participant']:
                    self.assertTrue(data_item.__contains__('session_creator_participant'))

                self.assertTrue(data_item.__contains__('id_creator_user'))
                if data_item['id_creator_user']:
                    self.assertTrue(data_item.__contains__('session_creator_user'))

                self.assertTrue(data_item.__contains__('id_session'))
                self.assertTrue(data_item.__contains__('id_session_type'))
                self.assertTrue(data_item.__contains__('session_comments'))
                self.assertTrue(data_item.__contains__('session_duration'))
                self.assertTrue(data_item.__contains__('session_name'))
                self.assertTrue(data_item.__contains__('session_start_datetime'))
                self.assertTrue(data_item.__contains__('session_status'))
                self.assertTrue(data_item.__contains__('session_uuid'))
                self.assertTrue(data_item.__contains__('session_participants'))
                self.assertTrue(data_item.__contains__('session_users'))

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
                self.assertTrue(data_item.__contains__('id_creator_device'))
                if data_item['id_creator_device']:
                    self.assertTrue(data_item.__contains__('session_creator_device'))

                self.assertTrue(data_item.__contains__('id_creator_participant'))
                if data_item['id_creator_participant']:
                    self.assertTrue(data_item.__contains__('session_creator_participant'))

                self.assertTrue(data_item.__contains__('id_creator_user'))
                if data_item['id_creator_user']:
                    self.assertTrue(data_item.__contains__('session_creator_user'))

                self.assertTrue(data_item.__contains__('id_session'))
                self.assertTrue(data_item.__contains__('id_session_type'))
                self.assertTrue(data_item.__contains__('session_comments'))
                self.assertTrue(data_item.__contains__('session_duration'))
                self.assertTrue(data_item.__contains__('session_name'))
                self.assertTrue(data_item.__contains__('session_start_datetime'))
                self.assertTrue(data_item.__contains__('session_status'))
                self.assertTrue(data_item.__contains__('session_uuid'))
                self.assertTrue(data_item.__contains__('session_participants'))
                self.assertTrue(data_item.__contains__('session_users'))

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
            self.assertEqual(response.status_code, 403)

    def test_query_with_limit(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera', params={'limit': 2})
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(2, len(response.json))

    def test_query_with_limit_and_offset(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera', params={'limit': 2, 'offset': 27})
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(1, len(response.json))

    def test_query_with_status(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera', params={'status': 0})
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(12, len(response.json))

            for data_item in response.json:
                self.assertEqual(0, data_item['session_status'])

    def test_query_with_limit_and_offset_and_status_and_list(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera',
                                                            params={'list': 1, 'limit': 2, 'offset': 11, 'status': 0})
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self.assertEqual(0, data_item['session_status'])

    def test_query_with_start_date_and_end_date(self):
        with self._flask_app.app_context():
            start_date = (datetime.now() - timedelta(days=6)).date().strftime("%Y-%m-%d")
            end_date = (datetime.now() - timedelta(days=4)).date().strftime("%Y-%m-%d")
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera',
                                                            params={'start_date': start_date, 'end_date': end_date})
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(6, len(response.json))

    def test_query_with_start_date(self):
        with self._flask_app.app_context():
            start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera', params={'start_date': start_date})
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(12, len(response.json))

    def test_query_with_end_date(self):
        with self._flask_app.app_context():
            end_date = (datetime.now() - timedelta(days=5)).date().strftime("%Y-%m-%d")
            response = response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                                       password='opentera',
                                                                       params={'end_date': end_date})
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(9, len(response.json))
