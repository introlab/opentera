from datetime import datetime, timedelta
from BaseParticipantAPITest import BaseParticipantAPITest
from modules.DatabaseModule.DBManagerTeraParticipantAccess import DBManagerTeraParticipantAccess
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSession import TeraSession
import uuid


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

            count = len(TeraSession.get_sessions_for_participant(
                part_id=TeraParticipant.get_participant_by_username('participant1').id_participant,
                limit=2, offset=27))

            self.assertEqual(count, len(response.json))

    def test_query_with_status(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera', params={'status': 0})
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])

            count = len(TeraSession.get_sessions_for_participant(
                part_id=TeraParticipant.get_participant_by_username('participant1').id_participant,
                status=0))

            self.assertEqual(count, len(response.json))

            for data_item in response.json:
                self.assertEqual(0, data_item['session_status'])

    def test_query_with_limit_and_offset_and_status_and_list(self):
        with self._flask_app.app_context():
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera',
                                                            params={'list': 1, 'limit': 2, 'offset': 11, 'status': 0})
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            count = len(TeraSession.get_sessions_for_participant(
                part_id=TeraParticipant.get_participant_by_username('participant1').id_participant,
                limit=2, offset=11, status=0))
            self.assertEqual(count, len(response.json))

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
            count = len(TeraSession.get_sessions_for_participant(
                part_id=TeraParticipant.get_participant_by_username('participant1').id_participant,
                start_date=datetime.now() - timedelta(days=6), end_date=datetime.now() - timedelta(days=4)))
            self.assertEqual(count, len(response.json))

    def test_query_with_start_date(self):
        with self._flask_app.app_context():
            start_date = (datetime.now() - timedelta(days=3)).date().strftime("%Y-%m-%d")
            response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                            password='opentera', params={'start_date': start_date})
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            count = len(TeraSession.get_sessions_for_participant(
                part_id=TeraParticipant.get_participant_by_username('participant1').id_participant,
                start_date=datetime.now() - timedelta(days=3)))
            self.assertEqual(count, len(response.json))

    def test_query_with_end_date(self):
        with self._flask_app.app_context():
            end_date = (datetime.now() - timedelta(days=5)).date().strftime("%Y-%m-%d")
            response = response = self._get_with_participant_http_auth(self.test_client, username='participant1',
                                                                       password='opentera',
                                                                       params={'end_date': end_date})
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            count = len(TeraSession.get_sessions_for_participant(
                part_id=TeraParticipant.get_participant_by_username('participant1').id_participant,
                end_date=end_date))
            self.assertEqual(count, len(response.json))

    def test_post_endpoint_with_valid_token_but_empty_schema(self):
        with self._flask_app.app_context():
            for participant in TeraParticipant.query.all():
                if not participant.participant_token:
                    continue
                response = self._post_with_participant_token_auth(self.test_client,
                                                                  token=participant.participant_token, json={})
                self.assertEqual(response.status_code, 400)

    def test_post_endpoint_with_valid_token_but_invalid_session(self):
        with self._flask_app.app_context():
            for participant in TeraParticipant.query.all():
                if not participant.participant_token:
                    continue
                # Get all participant ids
                participants_uuids = [participant.participant_uuid]

                # Invalid session schema
                session = {'session': {'id_session': 0, 'session_participants': participants_uuids}}
                response = self._post_with_participant_token_auth(self.test_client,
                                                                  token=participant.participant_token, json=session)
                self.assertEqual(response.status_code, 400)

    def test_post_endpoint_with_valid_token_valid_participants_valid_session_type_and_new_session(self):
        with self._flask_app.app_context():
            for participant in TeraParticipant.query.all():
                if not participant.participant_token:
                    continue
                participants_uuids = [participant.participant_uuid]

                access = DBManagerTeraParticipantAccess(participant)

                # Get all the session types available
                session_types = access.get_accessible_session_types_ids()

                for session_type in session_types:
                    session = {'session': {
                                    'id_session': 0,
                                    'session_participants': participants_uuids,
                                    'id_session_type': session_type,
                                    'session_name': 'TEST',
                                    'session_status': 0,
                                    'session_start_datetime': str(datetime.now())}}

                    response = self._post_with_participant_token_auth(self.test_client,
                                                                      token=participant.participant_token, json=session)

                    self.assertEqual(response.status_code, 200)
                    self.assertTrue('id_session' in response.json)
                    self.assertGreater(response.json['id_session'], 0)
                    self.assertEqual(response.json['id_creator_participant'], participant.id_participant)

    def test_post_endpoint_with_valid_token_invalid_participants_valid_session_type_and_new_session(self):
        with self._flask_app.app_context():
            for participant in TeraParticipant.query.all():
                if not participant.participant_token:
                    continue
                # Generate invalid participants
                participants_uuids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]

                access = DBManagerTeraParticipantAccess(participant)

                # Get all the session types available
                session_types = access.get_accessible_session_types_ids()

                for session_type in session_types:
                    session = {'session': {
                        'id_session': 0,
                        'session_participants': participants_uuids,
                        'id_session_type': session_type,
                        'session_name': 'TEST',
                        'session_status': 0,
                        'session_start_datetime': str(datetime.now())}}

                    response = self._post_with_participant_token_auth(self.test_client,
                                                                      token=participant.participant_token, json=session)
                    self.assertEqual(response.status_code, 400)

    def test_post_endpoint_with_valid_token_valid_participants_invalid_session_type_and_new_session(self):
        with self._flask_app.app_context():
            for participant in TeraParticipant.query.all():
                if not participant.participant_token:
                    continue
                # Get all participant ids
                participants_uuids = [participant.participant_uuid]

                access = DBManagerTeraParticipantAccess(participant)

                session_types = [5000, 0]

                for session_type in session_types:
                    session = {'session': {
                        'id_session': 0,
                        'session_participants': participants_uuids,
                        'id_session_type': session_type,
                        'session_name': 'TEST',
                        'session_status': 0,
                        'session_start_datetime': str(datetime.now())}}

                    response = self._post_with_participant_token_auth(self.test_client,
                                                                      token=participant.participant_token, json=session)

                    self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_valid_token_valid_participants_valid_session_type_and_update_session(self):
        with self._flask_app.app_context():
            for participant in TeraParticipant.query.all():
                if not participant.participant_token:
                    continue
                access = DBManagerTeraParticipantAccess(participant)

                # Get all available sessions
                sessions = access.get_accessible_sessions_ids()
                participants_uuids = [participant.participant_uuid]

                for id_session in sessions:
                    db_session = TeraSession.get_session_by_id(id_session)
                    session = {'session': {
                        'id_session': id_session,
                        'session_participants': participants_uuids,
                        'id_session_type': db_session.id_session_type,
                        'session_name': 'TEST-UPDATE',
                        'session_status': 0,
                        'session_start_datetime': str(datetime.now())}}

                    response = self._post_with_participant_token_auth(self.test_client,
                                                                      token=participant.participant_token, json=session)

                    if db_session.id_creator_participant is not participant.id_participant:
                        self.assertEqual(response.status_code, 403)
                        continue

                    self.assertEqual(response.status_code, 200)
                    self.assertTrue('id_session' in response.json)
                    self.assertGreater(response.json['id_session'], 0)
                    self.assertEqual(response.json['id_creator_participant'], participant.id_participant)
