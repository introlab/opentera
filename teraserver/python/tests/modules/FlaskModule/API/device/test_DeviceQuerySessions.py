from tests.modules.FlaskModule.API.device.BaseDeviceAPITest import BaseDeviceAPITest
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraSession import TeraSession
from modules.DatabaseModule.DBManagerTeraDeviceAccess import DBManagerTeraDeviceAccess
from datetime import datetime
import uuid


class DeviceQuerySessionsTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/sessions'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_with_invalid_token(self):
        with self._flask_app.app_context():
            response = self._get_with_device_token_auth(self.test_client, token='Invalid')
            self.assertEqual(response.status_code, 401)

    def test_get_endpoint_with_valid_token(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                # Devices should not be able to query sessions
                response = self._get_with_device_token_auth(self.test_client, token=device.device_token)
                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_valid_token_but_empty_schema(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json={})

                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 400)

    def test_post_endpoint_with_valid_token_but_invalid_session(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                # Get all participant ids
                participants_uuids = [participant.participant_uuid for participant in device.device_participants]

                # Invalid session schema
                session = {'session': {'id_session': 0, 'session_participants': participants_uuids}}
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json=session)

                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 400)

    def test_post_endpoint_with_valid_token_valid_participants_valid_session_type_and_new_session(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                # Get all participant ids
                participants_uuids = [participant.participant_uuid for participant in device.device_participants]

                access = DBManagerTeraDeviceAccess(device)

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

                    response = self._post_with_device_token_auth(self.test_client, token=device.device_token,
                                                                 json=session)

                    if not device.device_enabled:
                        self.assertEqual(response.status_code, 401)
                        continue

                    self.assertEqual(response.status_code, 200)
                    self.assertTrue('id_session' in response.json)
                    self.assertGreater(response.json['id_session'], 0)
                    self.assertEqual(response.json['id_creator_device'], device.id_device)

    def test_post_endpoint_with_valid_token_invalid_participants_valid_session_type_and_new_session(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                # Generate invalid participants
                participants_uuids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]

                access = DBManagerTeraDeviceAccess(device)

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

                    response = self._post_with_device_token_auth(self.test_client, token=device.device_token,
                                                                 json=session)

                    if not device.device_enabled:
                        self.assertEqual(response.status_code, 401)
                        continue

                    self.assertEqual(response.status_code, 400)

    def test_post_endpoint_with_valid_token_valid_participants_invalid_session_type_and_new_session(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                # Get all participant ids
                participants_uuids = [participant.participant_uuid for participant in device.device_participants]

                access = DBManagerTeraDeviceAccess(device)

                # Get all the session types available
                session_types = [5000]

                for session_type in session_types:
                    session = {'session': {
                        'id_session': 0,
                        'session_participants': participants_uuids,
                        'id_session_type': session_type,
                        'session_name': 'TEST',
                        'session_status': 0,
                        'session_start_datetime': str(datetime.now())}}

                    response = self._post_with_device_token_auth(self.test_client, token=device.device_token,
                                                                 json=session)

                    if not device.device_enabled:
                        self.assertEqual(response.status_code, 401)
                        continue

                    self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_valid_token_valid_participants_valid_session_type_and_update_session(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                access = DBManagerTeraDeviceAccess(device)

                # Get all available sessions
                sessions = access.get_accessible_sessions_ids()
                participants_uuids = [participant.participant_uuid for participant in device.device_participants]

                for id_session in sessions:
                    db_session = TeraSession.get_session_by_id(id_session)
                    session = {'session': {
                        'id_session': id_session,
                        'session_participants': participants_uuids,
                        'id_session_type': db_session.id_session_type,
                        'session_name': 'TEST-UPDATE',
                        'session_status': 0,
                        'session_start_datetime': str(datetime.now())}}

                    response = self._post_with_device_token_auth(self.test_client, token=device.device_token,
                                                                 json=session)

                    if not device.device_enabled:
                        self.assertEqual(response.status_code, 401)
                        continue

                    if db_session.id_creator_device is not device.id_device:
                        self.assertEqual(response.status_code, 403)
                        continue

                    self.assertEqual(response.status_code, 200)
                    self.assertTrue('id_session' in response.json)
                    self.assertGreater(response.json['id_session'], 0)
                    self.assertEqual(response.json['id_creator_device'], device.id_device)

    def test_delete_endpoint_with_valid_session_id(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                access = DBManagerTeraDeviceAccess(device)

                # Get all available sessions
                sessions = access.get_accessible_sessions_ids()

                for id_session in sessions:
                    response = self._delete_with_device_token_auth(self.test_client, token=device.device_token,
                                                                   params={'id_session': id_session})

                    self.assertEqual(response.status_code, 403)
