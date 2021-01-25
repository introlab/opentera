from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import random
from opentera.db.models.TeraDeviceType import TeraDeviceType


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
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_device_type'))
        self.assertTrue(json_data.__contains__('device_type_key'))
        self.assertTrue(json_data.__contains__('device_type_name'))

    def test_query_get_as_admin(self):
        params = {'id_device_type': 0, 'list': False}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        # Loop through device types
        for i in range(1, 4):

            params = {'id_device_type': i, 'list': False}
            response = self._request_with_http_auth(username='admin', password='admin', payload=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json()
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0])

            params = {'id_device_type': i, 'list': True}
            response = self._request_with_http_auth(username='admin', password='admin', payload=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json()
            self.assertEqual(len(json_data), 1)
            self._checkJson(json_data=json_data[0])

        params = {'id_device_type': 5, 'list': False}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 403)

    def test_query_post_as_admin(self):
        new_id = []
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        new_id.append(response.json()[0]['id_device_type'])

        # Create another instance of the same object - Fail Expected
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 500)

        # Create an instance of the same key - Fail expected
        params = {'device_type': {'device_type_name': 'New_Device_Type_2',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 500)

        # Create same name but different key ID = 8 - Pass expected
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device_2'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        new_id.append(response.json()[0]['id_device_type'])

        # update the key to a already created key- Fail expected
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': new_id[1],
                                  'device_type_key': 'new_device'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 500)

        # update the key to available key - pass expected
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': new_id[1],
                                  'device_type_key': 'new_device_3'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        new_id[1] = response.json()[0]['id_device_type']

        # update the name - Pass expected
        params = {'device_type': {'device_type_name': 'NEW_DEVICE_TYPE',
                                  'id_device_type': new_id[1],
                                  'device_type_key': 'new_device_3'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # Update the name of an unexisting device
        params = {'device_type': {'device_type_name': 'NEW_DEVICE_TYPE',
                                  'id_device_type': new_id[1]+1,
                                  'device_type_key': 'new_device_3'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 500)

        # Update the name of an unexisting device (no ID)
        params = {'device_type': {'device_type_name': 'NEW_DEVICE_TYPE',
                                  'id_device_type': None,
                                  'device_type_key': 'new_device_3'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 500)

        # Delete the objects created by the test
        params = {'device_type_key': 'new_device'}
        response = self._delete_with_http_auth_plus(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        params = {'device_type_key': 'new_device_3'}
        response = self._delete_with_http_auth_plus(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

    def test_query_post_as_user(self):
        # create new device without admin auth
        params = {'device_type': {'device_type_name': 'NEW_DEVICE_TYPE',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device'}}
        response = self._post_with_http_auth(username='user4', password='user4', payload=params)
        self.assertEqual(response.status_code, 403)

    def test_query_delete_as_admin(self):
        new_id = []
        # This test should be run on a clean server (i.e. with only the defaults created)
        # Else, the ID of the new devices created wont be aligned and the tests will fail
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        # new_id[0]
        new_id.append(response.json()[0]['id_device_type'])

        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device_1'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        # new_id[1]
        new_id.append(response.json()[0]['id_device_type'])

        # Delete without params
        params = {}
        response = self._delete_with_http_auth_plus(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 400)

        # Deleting the new device type
        params = {'device_type_key': 'new_device'}
        response = self._delete_with_http_auth_plus(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # Try deleting 2 devices at once
        params = {'id': new_id[1], 'device_type_key': 'new_device_2'}
        response = self._delete_with_http_auth_plus(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 400)

        # Deleting the new device 1 type
        params = new_id[1]
        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=params)
        self.assertEqual(response.status_code, 200)

        # Try deleting again an unexisting Device type
        params = {'id': new_id[1]}
        response = self._delete_with_http_auth_plus(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 500)

    def test_query_delete_as_user(self):

        params = {'device_type': {'device_type_name': 'NEW_DEVICE_TYPE',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        params = {'device_type_key': 'new_device'}
        response = self._delete_with_http_auth_plus(username='user4', password='user4', payload=params)
        self.assertEqual(response.status_code, 403)

        response = self._delete_with_http_auth_plus(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

