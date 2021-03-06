from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest


class UserQueryOnlineDevicesTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/devices/online'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_auth(self):
        response = self._request_with_no_auth()
        # Not authorized
        self.assertEqual(response.status_code, 401)

    def test_post_no_auth(self):
        response = self._post_with_no_auth()
        # Not allowed
        self.assertEqual(response.status_code, 405)

    def test_delete_no_auth(self):
        response = self._delete_with_no_auth(id_to_del=0)
        # Not allowed
        self.assertEqual(response.status_code, 405)

    def test_with_admin_auth(self):
        response = self._request_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 200)

        # Check for important status fields
        for device_info in response.json():
            self.assertTrue('device_online' in device_info)
            self.assertTrue('device_busy' in device_info)
            self.assertTrue('device_status' in device_info)
