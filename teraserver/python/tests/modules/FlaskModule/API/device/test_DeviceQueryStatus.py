from BaseDeviceAPITest import BaseDeviceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraSession import TeraSession
from modules.DatabaseModule.DBManagerTeraDeviceAccess import DBManagerTeraDeviceAccess
from datetime import datetime
import uuid
import json


class DeviceQueryStatusTest(BaseDeviceAPITest):
    test_endpoint = '/api/device/status'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import device_api_ns
        from BaseDeviceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.device.DeviceQueryStatus import DeviceQueryStatus
        kwargs = {
            'flaskModule': FakeFlaskModule(config=BaseDeviceAPITest.getConfig()),
            'test': True
        }
        device_api_ns.add_resource(DeviceQueryStatus, '/status', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_with_invalid_token(self):
        with flask_app.app_context():
            response = self._get_with_device_token_auth(self.test_client, token='Invalid')
            self.assertEqual(response.status_code, 405)

    def test_post_endpoint_with_no_payload_and_device_offline_should_fail(self):
        with flask_app.app_context():
            for device in TeraDevice.query.all():
                if device.device_onlineable and device.device_enabled:
                    self._simulate_device_offline(device)
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json={})
                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                    continue

                if not device.device_onlineable:
                    self.assertEqual(response.status_code, 403)
                    continue

                self.assertEqual(response.status_code, 400)

    def test_post_endpoint_with_valid_payload_and_device_offline_should_fail(self):
        with flask_app.app_context():
            for device in TeraDevice.query.all():
                if device.device_onlineable and device.device_enabled:
                    self._simulate_device_offline(device)
                schema = {'status': '{}', 'timestamp': int(datetime.now().timestamp())}
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json=schema)
                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                    continue

                if not device.device_onlineable:
                    self.assertEqual(response.status_code, 403)
                    continue

                self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_invalid_payload_and_device_online_should_fail(self):
        with flask_app.app_context():
            for device in TeraDevice.query.all():
                if device.device_onlineable and device.device_enabled:
                    self._simulate_device_online(device)
                schema = {'wrong_status': '{}', 'timestamp': int(datetime.now().timestamp())}
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json=schema)
                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                    continue

                if not device.device_onlineable:
                    self.assertEqual(response.status_code, 403)
                    continue

                self.assertEqual(response.status_code, 400)

                if device.device_onlineable and device.device_enabled:
                    self._simulate_device_offline(device)

    def test_post_endpoint_with_valid_payload_and_device_online_should_work(self):
        with flask_app.app_context():
            for device in TeraDevice.query.all():
                if device.device_onlineable and device.device_enabled:
                    self._simulate_device_online(device)
                schema = {'status': {'key': True}, 'timestamp': int(datetime.now().timestamp())}
                response = self._post_with_device_token_auth(self.test_client, token=device.device_token, json=schema)
                if not device.device_enabled:
                    self.assertEqual(response.status_code, 401)
                    continue

                if not device.device_onlineable:
                    self.assertEqual(response.status_code, 403)
                    continue

                self.assertEqual(response.status_code, 200)
                self._simulate_device_offline(device)
