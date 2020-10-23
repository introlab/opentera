from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import random
from libtera.db.models.TeraDeviceType import TeraDeviceType


class UserQueryDeviceTypesTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/devicesubtypes'

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

    def _checkJson(self, json_data, minimal=False):
        for js in json_data:
            self.assertGreater(len(js), 0)
            self.assertTrue(js.__contains__('device_subtype_name'))
            self.assertTrue(js.__contains__('id_device_subtype'))
            self.assertTrue(js.__contains__('id_device_type'))
            self.assertTrue(js.__contains__('device_subtype_parent'))

    def test_query_get_as_admin(self):
        params = {'id_device_type': 0, 'list': False}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 403)

        params = {'id_device_subtype': 1, 'list': False}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        self._checkJson(json_data=json_data)

        params = {'id_device_subtype': 2, 'list': True}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        self._checkJson(json_data=json_data)

        params = {'id_device_subtype': 5, 'list': False}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 403)

        params = {'id_device_type': 4, 'list': True}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self._checkJson(json_data=json_data)

    def test_query_post_as_admin(self):
        # {
        #     "device_subtype": {
        #         "device_subtype_name": "string",
        #         "id_device_subtype": 0,
        #         "id_device_type": 0
        #     }
        # }
        new_id = []
        params = {'device_subtype': {'device_subtype_name': 'New_Device_Subtype', 'id_device_subtype': 0,
                                     'id_device_type': 2}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        new_id.append(response.json()[0]['id_device_subtype'])
        self._checkJson(json_data=response.json())

        # Create same name but different id_device_type = 8 - Pass expected
        params = {'device_subtype': {'device_subtype_name': 'New_Device_Subtype', 'id_device_subtype': 0,
                                     'id_device_type': 3}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        new_id.append(response.json()[0]['id_device_subtype'])
        self._checkJson(json_data=response.json())

        # Create id_device_type wrong - 500 expected
        params = {'device_subtype': {'device_subtype_name': 'New_Device_Subtype', 'id_device_subtype': 0,
                                     'id_device_type': 10}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 500)

        # update name without id_device_type, accepted
        params = {'device_subtype': {'device_subtype_name': 'New_Device_Subtype_2', 'id_device_subtype': new_id[0]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)

        # update the name - Pass expected
        params = {'device_subtype': {'id_device_subtype': new_id[0], 'id_device_type': 2,
                                     'device_subtype_name': 'New_Device_Subtype_2'}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self._checkJson(json_data=response.json())

        # Update the ID of an unexisting device
        params = {'device_subtype': {'device_subtype_name': 'New_Device_Subtype', 'id_device_subtype': new_id[1]+1,
                                     'id_device_type': 3}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 500)

        # Delete the objects created by the test
        for id_to_del in new_id:
            response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=id_to_del)
            self.assertEqual(response.status_code, 200)

    def test_query_post_as_user(self):
        params = {'device_subtype': {'device_subtype_name': 'New_Device_Subtype', 'id_device_subtype': 0,
                                     'id_device_type': 2}}
        response = self._post_with_http_auth(username='user4', password='user4', payload=params)
        self.assertEqual(response.status_code, 403)

    def test_query_delete_as_admin(self):
        params = {'device_subtype': {'device_subtype_name': 'New_Device_Subtype', 'id_device_subtype': 0,
                                     'id_device_type': 2}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        new_id = response.json()[0]['id_device_subtype']
        self._checkJson(json_data=response.json())

        # Delete without param
        params = {}
        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=new_id+1)
        self.assertEqual(response.status_code, 400)

        # Deleting the new device type
        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=new_id)
        self.assertEqual(response.status_code, 200)

    def test_query_delete_as_user(self):
        params = {'device_subtype': {'device_subtype_name': 'New_Device_Subtype', 'id_device_subtype': 0,
                                     'id_device_type': 2}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        new_id = response.json()[0]['id_device_subtype']
        self._checkJson(json_data=response.json())

        response = self._delete_with_http_auth(username='user4', password='user4', id_to_del=new_id)
        self.assertEqual(response.status_code, 403)

        # Deleting the new device type
        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=new_id)
        self.assertEqual(response.status_code, 200)


