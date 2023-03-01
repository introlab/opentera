from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraDevice import TeraDevice


class UserQueryDeviceTypesTest(BaseUserAPITest):
    test_endpoint = '/api/user/devicetypes'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(response.status_code, 401)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.delete(self.test_endpoint)
            self.assertEqual(response.status_code, 401)

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            target_count = TeraDeviceType.get_count()
            self.assertEqual(len(json_data), target_count)

            for data_item in json_data:
                self._checkJson(data_item)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_device_type'))
        self.assertTrue(json_data.__contains__('device_type_key'))
        self.assertTrue(json_data.__contains__('device_type_name'))

    def test_query_get_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_device_type': 0, 'list': False}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            device_types = TeraDeviceType.query.all()
            # Loop through device types
            for device_type in device_types:

                params = {'id_device_type': device_type.id_device_type, 'list': False}
                response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                         params=params)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers['Content-Type'], 'application/json')
                json_data = response.json
                self.assertEqual(len(json_data), 1)
                self._checkJson(json_data=json_data[0])
                self.assertEqual(device_type.device_type_name, json_data[0]['device_type_name'])

                params = {'id_device_type': device_type.id_device_type, 'list': True}
                response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                         params=params)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers['Content-Type'], 'application/json')
                json_data = response.json
                self.assertEqual(len(json_data), 1)
                self._checkJson(json_data=json_data[0], minimal=True)
                self.assertEqual(device_type.device_type_name, json_data[0]['device_type_name'])

    def test_query_post_as_admin(self):
        new_id = []
        params = {'device_type_name': 'New_Device_Type', 'device_type_key': 'new_device', 'id_device_type': 0}

        # Missing device_type
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                  json=params)
        self.assertEqual(response.status_code, 400)

        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'device_type_key': 'new_device'}}

        # Missing id_device_type
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                  json=params)
        self.assertEqual(response.status_code, 400)

        params['device_type']['id_device_type'] = 0
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                  json=params)
        self.assertEqual(response.status_code, 200)
        new_id.append(response.json[0]['id_device_type'])

        # Create another instance of the same object - Fail Expected
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 500)

        # Create an instance of the same key - Fail expected
        params = {'device_type': {'device_type_name': 'New_Device_Type_2',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device'}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 500)

        # Create same name but different key ID = 8 - Pass expected
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device_2'}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 200)
        new_id.append(response.json[0]['id_device_type'])

        # update the key to an already created key - Fail expected
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': new_id[1],
                                  'device_type_key': 'new_device'}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 500)

        # update the key to available key - pass expected
        params = {'device_type': {'device_type_name': 'New_Device_Type',
                                  'id_device_type': new_id[1],
                                  'device_type_key': 'new_device_3'}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 200)
        new_id[1] = response.json[0]['id_device_type']

        # update the name - Pass expected
        params = {'device_type': {'device_type_name': 'NEW_DEVICE_TYPE',
                                  'id_device_type': new_id[1],
                                  'device_type_key': 'new_device_3'}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 200)

        # Update the name of a non-existing device
        params = {'device_type': {'device_type_name': 'NEW_DEVICE_TYPE',
                                  'id_device_type': new_id[1]+1,
                                  'device_type_key': 'new_device_3'}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 400)

        # Update the name of an unexisting device (no ID)
        params = {'device_type': {'device_type_name': 'NEW_DEVICE_TYPE',
                                  'id_device_type': None,
                                  'device_type_key': 'new_device_3'}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 400)

        # Delete the objects created by the test
        params = {'device_type_key': 'new_device'}
        response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)

        params = {'device_type_key': 'new_device_3'}
        response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)

    def test_query_post_as_user(self):
        # create new device without admin auth
        params = {'device_type': {'device_type_name': 'NEW_DEVICE_TYPE',
                                  'id_device_type': 0,
                                  'device_type_key': 'new_device'}}
        response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4', json=params)
        self.assertEqual(response.status_code, 403)

        response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                  json=params)
        self.assertEqual(response.status_code, 403)

    def test_query_delete_as_admin(self):
        with self._flask_app.app_context():
            device_type = TeraDeviceType()
            device_type.device_type_name = 'Test1234'
            device_type.device_type_key = 'Test Device Type'
            TeraDeviceType.insert(device_type)

            device = TeraDevice()
            device.id_device_type = device_type.id_device_type
            device.device_name = 'Test Device'
            TeraDevice.insert(device)

            # Deleting device type with device associated
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': device_type.id_device_type})
            self.assertEqual(response.status_code, 500)

            # Try deleting 2 devices at once
            params = {'id': device_type.id_device_type, 'device_type_key': 'Test Device Type'}
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(response.status_code, 400)

            # Deleting the device, and then the device type
            TeraDevice.delete(device.id_device)
            device_type_id = device_type.id_device_type
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': device_type.id_device_type})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(TeraDeviceType.get_device_type_by_id(device_type_id), None)

    def test_query_delete_as_user(self):
        with self._flask_app.app_context():
            device_type = TeraDeviceType()
            device_type.device_type_name = 'Test1234'
            device_type.device_type_key = 'Test Device Type'
            TeraDeviceType.insert(device_type)

            device_type_id = device_type.id_device_type

            params = {'id': device_type_id}
            # No access user
            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params=params)
            self.assertEqual(response.status_code, 403)

            # Not site admin
            response = self._delete_with_user_http_auth(self.test_client, username='user3', password='user3',
                                                        params=params)
            self.assertEqual(response.status_code, 403)

            # Site admin
            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params=params)
            self.assertEqual(response.status_code, 403)

            # Super admin
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(response.status_code, 200)
