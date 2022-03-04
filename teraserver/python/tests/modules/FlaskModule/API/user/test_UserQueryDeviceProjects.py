from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest


class UserQueryDeviceProjectsTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/deviceprojects'

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

    def test_query_as_user(self):
        response = self._request_with_http_auth(username='user', password='user', payload="")
        self.assertEqual(response.status_code, 400)

    def test_query_project_as_admin(self):
        params = {'id_project': 10}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_project': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_project_with_devices_as_admin(self):
        params = {'id_project': 1, 'with_devices': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_device_as_admin(self):
        params = {'id_device': 30}  # Invalid service
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_device': 2}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_device_with_projects_as_admin(self):
        params = {'id_device': 1, 'with_projects': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 3)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_device_with_projects_and_with_sites_as_admin(self):
        params = {'id_device': 3, 'with_projects': 1, 'with_sites': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 3)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('id_site'))
            self.assertTrue(data_item.__contains__('site_name'))

    def test_query_list_as_admin(self):
        params = {'id_project': 1, 'list': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_project_as_user(self):
        params = {'id_project': 10}
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_project': 1}
        response = self._request_with_http_auth(username='user4', password='user4', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_project': 1}
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_project_with_devices_as_user(self):
        params = {'id_project': 1, 'with_devices': 1}
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_device_as_user(self):
        params = {'id_device': 30}  # Invalid
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_device': 1}
        response = self._request_with_http_auth(username='user4', password='user4', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_device': 2}
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_device_with_projects_as_user(self):
        params = {'id_device': 1, 'with_projects': 1}
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        params = {'id_device': 2, 'list': 1}

        response = self._request_with_http_auth(username='user4', password='user4', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_post_device(self):
        # New with minimal infos
        json_data = {}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing everything")  # Missing

        json_data = {'device': {}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_service")

        json_data = {'device': {'id_device': 1}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing projects")

        json_data = {'device': {'id_device': 1, 'projects': []}}
        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Only project/site admins can change things here")

        json_data = {'device': {'id_device': 2, 'projects': []}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove from all projects OK")

        params = {'id_device': 2}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)  # Everything was deleted!

        json_data = {'device': {'id_device': 2, 'projects': [{'id_project': 1},
                                                             {'id_project': 2},
                                                             {'id_project': 3}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="One project not part of device site")

        json_data = {'device': {'id_device': 2, 'projects': [{'id_project': 1},
                                                             {'id_project': 2}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Add all projects OK")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)  # Everything was added

        json_data = {'device': {'id_device': 2, 'projects': [{'id_project': 1}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove one project")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

    def test_post_project(self):
        # Project update
        json_data = {'project': {}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_project")

        json_data = {'project': {'id_project': 1}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing devices")

        json_data = {'project': {'id_project': 1, 'devices': []}}
        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

        json_data = {'project': {'id_project': 1, 'devices': []}}
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove all devices OK")

        params = {'id_project': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)  # Everything was deleted!

        json_data = {'project': {'id_project': 1, 'devices': [{'id_device': 1},
                                                              {'id_device': 2},
                                                              {'id_device': 3}]}}
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="One device not allowed - not part of the site project!")

        json_data = {'project': {'id_project': 1, 'devices': [{'id_device': 1},
                                                              {'id_device': 2}]}}
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="New device association OK")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)  # Everything was added

        json_data = {'project': {'id_project': 1, 'devices': [{'id_device': 1}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove 1 device")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        json_data = {'project': {'id_project': 1, 'devices': [{'id_device': 1},
                                                              {'id_device': 2}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Back to initial state")

    def test_post_device_project_and_delete(self):
        # Device-Project update
        json_data = {'device_project': {}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Badly formatted request")

        json_data = {'device_project': {'id_project': 1}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Badly formatted request")

        json_data = {'device_project': {'id_project': 1, 'id_device': 1}}
        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

        json_data = {'device_project': {'id_project': 1, 'id_device': 3}}
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Add new association not OK - device not part of the site")

        params = {'id_project': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()

        current_id = None
        for dp in json_data:
            if dp['id_device'] == 2:
                current_id = dp['id_device_project']
                break
        self.assertFalse(current_id is None)

        # Delete current association before adding it
        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Current association deleted")

        json_data = {'device_project': {'id_project': 1, 'id_device': 2}}
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Add new association OK")

        params = {'id_project': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        current_id = None
        for dp in json_data:
            if dp['id_device'] == 1:
                current_id = dp['id_device_project']
                break
        self.assertFalse(current_id is None)

        response = self._delete_with_http_auth(username='user', password='user', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='siteadmin', password='siteadmin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

        params = {'id_project': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        json_data = {'device': {'id_device': 1, 'projects': [{'id_project': 1},
                                                             {'id_project': 2}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Back to initial state")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_device_project'))
        self.assertTrue(json_data.__contains__('id_device'))
        self.assertTrue(json_data.__contains__('id_project'))

        if not minimal:
            self.assertTrue(json_data.__contains__('device_name'))
            self.assertTrue(json_data.__contains__('device_available'))
            self.assertTrue(json_data.__contains__('project_name'))
        else:
            self.assertFalse(json_data.__contains__('device_name'))
            self.assertFalse(json_data.__contains__('device_available'))
            self.assertFalse(json_data.__contains__('project_name'))
