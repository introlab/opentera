from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
from datetime import datetime
from websocket import create_connection
import ssl


class DeviceQueryStatusTest(BaseAPITest):
    login_endpoint = '/api/device/login'
    test_endpoint = '/api/device/status'
    devices = []

    def setUp(self):
        # Query all enabled devices
        params = {}
        response = self._request_with_http_auth('admin', 'admin', params, '/api/user/devices')
        self.assertEqual(response.status_code, 200)
        self.devices = response.json()
        self.assertGreater(len(self.devices), 0)

    def tearDown(self):
        pass

    def _login_device(self, token: str, should_fail=False):
        result = self._login_with_token(token)
        if should_fail:
            self.assertNotEqual(200, result.status_code)
        else:
            self.assertEqual(200, result.status_code)
        return result.json()

    def test_send_status_with_no_payload_should_fail(self):
        for dev in self.devices:
            self.assertTrue('device_onlineable' in dev)
            self.assertTrue('device_enabled' in dev)
            self.assertTrue('device_token' in dev)

            if dev['device_enabled']:
                answer = self._post_with_token(dev['device_token'], payload=None)
                self.assertEqual(400, answer.status_code)

    def test_malformed_status_should_fail(self):
        for dev in self.devices:
            self.assertTrue('device_onlineable' in dev)
            self.assertTrue('device_enabled' in dev)
            self.assertTrue('device_token' in dev)

            if dev['device_enabled']:
                device_status = {
                    'wrong_status': {'field': True},
                    'timestamp': datetime.now().timestamp()
                }
                answer = self._post_with_token(dev['device_token'], payload=device_status)
                self.assertEqual(400, answer.status_code)

    def test_send_status_with_disabled_devices_should_fail(self):
        for dev in self.devices:
            self.assertTrue('device_onlineable' in dev)
            self.assertTrue('device_enabled' in dev)
            self.assertTrue('device_token' in dev)

            if not dev['device_enabled']:
                device_status = {
                    'status': {'field': True},
                    'timestamp': datetime.now().timestamp()
                }
                answer = self._post_with_token(dev['device_token'], payload=device_status)
                self.assertEqual(401, answer.status_code)

    def test_send_status_with_offline_devices_should_fail(self):
        for dev in self.devices:
            self.assertTrue('device_token' in dev)

            if dev['device_onlineable'] and dev['device_enabled']:
                device_status = {
                    'status': {'field': True},
                    'timestamp': datetime.now().timestamp()
                }
                answer = self._post_with_token(dev['device_token'], payload=device_status)
                self.assertNotEqual(200, answer.status_code)

    def test_send_status_with_wrong_payload_online_device_should_fail(self):
        for dev in self.devices:
            self.assertTrue('device_token' in dev)

            if dev['device_onlineable'] and dev['device_enabled']:
                login_info = self._login_device(dev['device_token'])
                self.assertTrue('websocket_url' in login_info)
                # Connect websocket, not verifying ssl
                ws = create_connection(login_info['websocket_url'], sslopt={'cert_reqs': ssl.CERT_NONE})
                self.assertTrue(ws.connected)

                device_status = {
                    'wrong_status': {'field': True},
                    'timestamp': datetime.now().timestamp()
                }
                answer = self._post_with_token(dev['device_token'], payload=device_status)
                self.assertEqual(400, answer.status_code)

    def test_send_satus_with_good_payload_online_device_should_work(self):
        for dev in self.devices:
            self.assertTrue('device_token' in dev)

            if dev['device_onlineable'] and dev['device_enabled']:
                login_info = self._login_device(dev['device_token'])
                self.assertTrue('websocket_url' in login_info)
                # Connect websocket, not verifying ssl
                ws = create_connection(login_info['websocket_url'], sslopt={'cert_reqs': ssl.CERT_NONE})
                self.assertTrue(ws.connected)

                device_status = {
                    'status': {'field': True},
                    'timestamp': datetime.now().timestamp()
                }

                answer = self._post_with_token(dev['device_token'], payload=device_status)
                self.assertEqual(200, answer.status_code)
                result = answer.json()
                uuid = result['uuid']
                self.assertEqual(dev['device_uuid'], uuid)
                del result['uuid']
                # self.assertEqual(result, device_status)
                ws.close()
