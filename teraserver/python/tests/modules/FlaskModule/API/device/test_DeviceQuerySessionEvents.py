from BaseDeviceAPITest import BaseDeviceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionEvent import TeraSessionEvent
from datetime import datetime


class DeviceQuerySessionEventsTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/sessionevents'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import device_api_ns
        from BaseDeviceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.device.DeviceQuerySessionEvents import DeviceQuerySessionEvents
        kwargs = {
            'flaskModule': FakeFlaskModule(config=BaseDeviceAPITest.getConfig()),
            'test': True
        }
        device_api_ns.add_resource(DeviceQuerySessionEvents, '/sessionevents', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_with_invalid_token(self):
        with flask_app.app_context():
            response = self._get_with_device_token_auth(self.test_client, token='Invalid')
            self.assertEqual(response.status_code, 401)

    def test_get_endpoint_with_valid_token(self):
        with flask_app.app_context():
            for device in TeraDevice.query.all():
                response = self._get_with_device_token_auth(self.test_client, token=device.device_token)

                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_empty_schema(self):
        with flask_app.app_context():
            for device in TeraDevice.query.all():
                schema = {}
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json={})
                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 400)

    def test_post_endpoint_with_empty_session_event(self):
        with flask_app.app_context():
            for device in TeraDevice.query.all():
                schema = {'session_event': {}}
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json=schema)
                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 400)

    def test_post_endpoint_with_invalid_session_id_and_id_session_event(self):
        with flask_app.app_context():
            for device in TeraDevice.query.all():
                schema = {'session_event': {'id_session': -1, 'id_session_event': -1}}
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json=schema)
                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_valid_session_id_and_new_session_event(self):
        with flask_app.app_context():
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
        with flask_app.app_context():
            for device in TeraDevice.query.all():
                for session in device.device_sessions:
                    for event in session.session_events:
                        schema = {'session_event': event.to_json(minimal=False)}

                        # Update time
                        schema['session_event']['session_event_datetime'] = str(datetime.now())

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
