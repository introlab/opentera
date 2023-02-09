from BaseDeviceAPITest import BaseDeviceAPITest
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionEvent import TeraSessionEvent
from datetime import datetime


class DeviceQuerySessionEventsTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/sessions/events'

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
                response = self._get_with_device_token_auth(self.test_client, token=device.device_token)

                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_empty_schema(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json={})
                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 400)

    def test_post_endpoint_with_empty_session_event(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                schema = {'session_event': {}}
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json=schema)
                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 400)

    def test_post_endpoint_with_invalid_session_id_and_id_session_event(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                schema = {'session_event': {'id_session': -1, 'id_session_event': -1}}
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json=schema)
                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_valid_session_id_and_new_session_event(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                for session in device.device_sessions:
                    schema = {'session_event': {'id_session': session.id_session,
                                                'id_session_event': -1,
                                                'id_session_event_type':
                                                    TeraSessionEvent.SessionEventTypes.DEVICE_EVENT.value,
                                                'session_event_datetime': str(datetime.now()),
                                                'session_event_text': 'session_event_text',

                                                'session_event_context': 'session_event_context'
                                                }
                              }

                    response = self._post_with_device_token_auth(self.test_client, token=device.device_token,
                                                                 json=schema)
                    if not device.device_enabled:
                        self.assertEqual(response.status_code, 401)
                        continue

                    # Test if the device owns the session, otherwise cannot add events
                    if session.id_creator_device == device.id_device:
                        self.assertEqual(response.status_code, 200)
                    else:
                        self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_valid_session_id_and_update_session_event(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                for session in TeraSession.query.all():

                    schema = {'session_event': {'id_session': session.id_session,
                                                'id_session_event_type': 1,
                                                'id_session_event': 0,  # New!
                                                'session_event_datetime': str(datetime.now())}
                              }

                    response = self._post_with_device_token_auth(self.test_client, token=device.device_token,
                                                                 json=schema)
                    if not device.device_enabled:
                        self.assertEqual(401, response.status_code)
                        continue

                    session_devices = [dev.id_device for dev in session.session_devices]

                    print('***403 ', device.id_device, session_devices)

                    # Test if the device owns the session, otherwise cannot add events
                    if device.id_device in session_devices:
                        self.assertEqual(200, response.status_code)
                    else:
                        self.assertEqual(403, response.status_code)
