from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
from libtera.db.models.TeraDeviceType import TeraDeviceType


class UserQueryDeviceTypesTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/devicetypes'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_auth(self):
        response = self._request_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_post_no_auth(self):
        response = self._post_with_no_auth()
        self.assertEqual(response.status_code, 401)

    def test_delete_no_auth(self):
        response = self._delete_with_no_auth(id_to_del=0)
        self.assertEqual(response.status_code, 401)

    def test_query_no_params_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin')
        self.assertEqual(response.status_code, 400)

    def test_query_get_as_admin(self):
        params = {'id_device_type': 0, 'list': False}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        params = {'id_device_type': 0, 'list': True}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 4)

        for i in range(3):
            params = {'id_device_type': i+1, 'list': False}
            response = self._request_with_http_auth(username='admin', password='admin', payload=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json()
            self.assertEqual(len(json_data), 1)

            params = {'id_device_type': i+1, 'list': True}
            response = self._request_with_http_auth(username='admin', password='admin', payload=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json()
            self.assertEqual(len(json_data), 4)

        params = {'id_device_type': 5, 'list': False}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 403)

    def test_post_as_admin(self):
        params = {'device_type': {'device_type_name': 'New_Device_Type', 'id_device_type': 0,\
                                  'device_type_key': 'new_device'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # Create another instance of the same object
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 501)

        # Delete the object created by the test
        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=20)
        self.assertEqual(response.status_code, 200)

    # def test_delete_as_admin(self):
        # Create a new device type
        # params = {'device_type': {'device_type_name': 'New_Device_Type', 'id_device_type': 0}}
        # self._post_with_http_auth(username='admin', password='admin', payload=params)

        # Deleting the new device type
        # params = 'New_Device_Type'
        # response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=16)
        # self.assertEqual(response.status_code, 200)

        # Try to delete again the same device
        # response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=5)
        # self.assertEqual(response.status_code, 500)

        # Try to delete with a device type without the power
        # response = self._delete_with_http_auth(username='user1', password='user1', id_to_del=1)
        # self.assertEqual(response.status_code, 403)
    #
    # def _delete_with_http_auth_by_name(self, username: str, password: str, device_type_name: str):
    #     device_type = TeraDeviceType.get_device_type_by_name(device_type_name)
    #     return self._delete_with_http_auth(username=username, password=password, id_to_del=device_type.id_device_type)




