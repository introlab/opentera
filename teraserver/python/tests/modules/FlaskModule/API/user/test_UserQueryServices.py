from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest
import datetime


class UserQueryServicesTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/services'

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
        self.assertEqual(len(json_data), 3)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="")
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

    def test_query_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertNotEqual(data_item['id_service'], 2) # Logger service should not be here since a system service!

    def test_query_list_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="list=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_list_with_project_as_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload={"list": True, 'with_projects': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_service=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)  # OpenTera service is a system service, and should not be returned here!

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_service=4")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        service_uuid = None
        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_service'], 4)
            service_uuid = data_item['service_uuid']

        # Now try to query with service uuid
        response = self._request_with_http_auth(username='admin', password='admin', payload="uuid=" + service_uuid)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['id_service'], 4)
            self.assertEqual(data_item['service_uuid'], service_uuid)

    def test_query_services_for_project_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_project=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_by_key_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="key=VideoRehabService")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertEqual(data_item['service_key'], 'VideoRehabService')

    def test_query_with_config_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="with_config=1&list=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreaterEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'service': {
                    "service_clientendpoint": "/",
                    "service_enabled": True,
                    "service_endpoint": "/test",
                    "service_hostname": "localhost",
                    "service_name": "Test",
                    "service_port": 0,
                    "service_config_schema": "{"
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_service")  # Missing id_service

        json_data['service']['id_service'] = 0
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 500, msg="Missing service_key")

        json_data['service']['service_key'] = 'Test'
        # response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        # self.assertEqual(response.status_code, 400, msg="Invalid insert service_config_schema")

        del json_data['service']['service_config_schema'] # Will use default value
        response = self._post_with_http_auth(username='user4', password='user4', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

        json_data = response.json()[0]
        self._checkJson(json_data)
        current_id = json_data['id_service']

        json_data = {
            'service': {
                'id_service': current_id,
                'service_enabled': False,
                'service_system': True,
                "service_name": "Test2",
                'service_config_schema': '{Test'
            }
        }
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post update with service_system that shouldn't be here")

        del json_data['service']['service_system']
        # response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        # self.assertEqual(response.status_code, 400, msg="Post update with invalid config schema")

        del json_data['service']['service_config_schema']
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update OK")
        json_data = response.json()[0]
        self._checkJson(json_data)
        self.assertEqual(json_data['service_enabled'], False)
        self.assertEqual(json_data['service_name'], 'Test2')

        response = self._delete_with_http_auth(username='user4', password='user4', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('service_uuid'))
        self.assertTrue(json_data.__contains__('service_name'))
        self.assertTrue(json_data.__contains__('service_key'))
        self.assertTrue(json_data.__contains__('service_hostname'))
        self.assertTrue(json_data.__contains__('service_port'))
        self.assertTrue(json_data.__contains__('service_endpoint'))
        self.assertTrue(json_data.__contains__('service_clientendpoint'))
        self.assertTrue(json_data.__contains__('service_enabled'))
        self.assertTrue(json_data.__contains__('service_editable_config'))

        if not minimal:
            self.assertTrue(json_data.__contains__('service_roles'))
            # self.assertTrue(json_data.__contains__('service_editable_config'))
        else:
            self.assertFalse(json_data.__contains__('service_roles'))
            # self.assertFalse(json_data.__contains__('service_editable_config'))
