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
        # This test should be run on a clean server (i.e. with only the defaults created)
        # Else, the ID of the new devices created wont be aligned and the tests will fail

        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # Create another instance of the same object - Fail Expected
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 501)

        # Create an instance of the same key - Fail expected
        params = {'device_type': {'device_type_name': 'New_Device_Type_2',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 501)

        # Create same name but different key ID = 8 - Pass expected
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device_2'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # update the key to key already created - Fail expected
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 8,
                                  'device_type_key': 'new_device'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 500)

        # update the key to key already created - pass expected
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 8,
                                  'device_type_key': 'new_device_3'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # update the name - Pass expexted
        params = {'device_type': {'device_type_name': 'NEW_DEVICE_TYPE',
                                  'id_device_type': 8,
                                  'device_type_key': 'new_device_3'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # Delete the object created by the test
        params = {'device_type_key': 'new_device'}
        response = self._delete_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        params = {'device_type_key': 'new_device_3'}
        response = self._delete_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

    def test_delete_as_admin(self):
        # This test should be run on a clean server (i.e. with only the defaults created)
        # Else, the ID of the new devices created wont be aligned and the tests will fail
        # Create a new device type ID = 5
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # ID = 6
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device_1'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # ID = 7
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device_2'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # Delete without params
        params = {}
        response = self._delete_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 500)

        # Deleting the new device type
        params = {'device_type_key': 'new_device'}
        response = self._delete_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # Deleting the new device 1 type
        params = {'id_device_type': 6}
        response = self._delete_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # Try deleting again an unexisting Device type
        params = {'id_device_type': 6}
        response = self._delete_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 500)

        # Try deleting 2 devices at once
        params = {'id_device_type': 7, 'device_type_key': 'capteur'}
        response = self._delete_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 501)

        # Deleting the same device with 2 parameters
        params = {'id_device_type': 7, 'device_type_key': 'new_device_2'}
        response = self._delete_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

    def _delete_with_http_auth(self, username, password, payload=None):
        from requests import delete
        if payload is None:
            payload = {}
        url = self._make_url(self.host, self.port, self.test_endpoint)
        return delete(url=url, verify=False, auth=(username, password), params=payload)


