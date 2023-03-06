from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraDeviceProject import TeraDeviceProject
from opentera.db.models.TeraDeviceSite import TeraDeviceSite


class UserQueryDeviceProjectsTest(BaseUserAPITest):
    test_endpoint = '/api/user/deviceprojects'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            with self._flask_app.app_context():
                response = self.test_client.get(self.test_endpoint)
                self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            with self._flask_app.app_context():
                response = self._get_with_user_http_auth(self.test_client)
                self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            with self._flask_app.app_context():
                response = self._get_with_user_token_auth(self.test_client)
                self.assertEqual(401, response.status_code)

    def test_post_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.post(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            params = {'id': 0}
            response = self.test_client.delete(self.test_endpoint, query_string=params)
            self.assertEqual(401, response.status_code)

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(400, response.status_code)

    def test_query_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user')
            self.assertEqual(400, response.status_code)

    def test_query_project_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 10}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_project_with_devices_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'with_devices': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 2)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_device_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_device': 30}  # Invalid service
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 0)

            params = {'id_device': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_device_with_projects_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_device': 1, 'with_projects': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 3)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_device_with_projects_and_with_sites_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_device': 3, 'with_projects': 1, 'with_sites': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 3)

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('id_site'))
                self.assertTrue(data_item.__contains__('site_name'))

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'list': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])

            self.assertEqual(len(response.json), 2)

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_project_as_user(self):
        with self._flask_app.app_context():
            params = {'id_project': 10}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 0)

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 0)

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 2)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_project_with_devices_as_user(self):
        with self._flask_app.app_context():
            params = {'id_project': 1, 'with_devices': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 2)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_device_as_user(self):
        with self._flask_app.app_context():
            params = {'id_device': 30}  # Invalid
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 0)

            params = {'id_device': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 0)

            params = {'id_device': 2}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_device_with_projects_as_user(self):
        with self._flask_app.app_context():
            params = {'id_device': 1, 'with_projects': 1}
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 2)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        with self._flask_app.app_context():
            params = {'id_device': 2, 'list': 1}

            response = self._get_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='user', password='user', params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/json', response.headers['Content-Type'])
            self.assertEqual(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_post_device(self):
        with self._flask_app.app_context():
            # Create "empty" associations with device
            ds = TeraDeviceSite()
            ds.id_device = 3
            ds.id_site = 1
            ds = TeraDeviceSite.insert(ds)

            dp1 = TeraDeviceProject()
            dp1.id_project = 1
            dp1.id_device = 3
            dp1 = TeraDeviceProject.insert(dp1)

            dp2 = TeraDeviceProject()
            dp2.id_project = 2
            dp2.id_device = 3
            dp2 = TeraDeviceProject.insert(dp2)

            # New with minimal infos
            json_data = {}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing everything")  # Missing

            json_data = {'device': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service")

            json_data = {'device': {'id_device': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing projects")

            json_data = {'device': {'id_device': 1, 'projects': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only project/site admins can change things here")

            json_data = {'device': {'id_device': 2, 'projects': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(500, response.status_code, msg="Can't remove from project - associated to participants.")

            json_data = {'device': {'id_device': 3, 'projects': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove all OK.")

            params = {'id_device': 3}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 0)  # Everything was deleted!

            json_data = {'device': {'id_device': 3, 'projects': [{'id_project': 1},
                                                                 {'id_project': 2},
                                                                 {'id_project': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="One project not part of device site")

            json_data = {'device': {'id_device': 3, 'projects': [{'id_project': 1},
                                                                 {'id_project': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all projects OK")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 2)  # Everything was added

            json_data = {'device': {'id_device': 3, 'projects': [{'id_project': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove one project")
            self.assertIsNone(TeraDeviceProject.get_device_project_id_for_device_and_project(3, 2))
            self.assertIsNotNone(TeraDeviceProject.get_device_project_id_for_device_and_project(3, 1))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            # Back to initial state
            TeraDeviceProject.delete(dp1.id_device_project)  # dp2 = already deleted
            TeraDeviceSite.delete(ds.id_device_site)

    def test_post_project(self):
        with self._flask_app.app_context():
            # Create "empty" associations with device
            dp1 = TeraDeviceProject()
            dp1.id_project = 2
            dp1.id_device = 1
            dp1 = TeraDeviceProject.insert(dp1)

            dp2 = TeraDeviceProject()
            dp2.id_project = 2
            dp2.id_device = 2
            dp2 = TeraDeviceProject.insert(dp2)

            # Project update
            json_data = {'project': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_project")

            json_data = {'project': {'id_project': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing devices")

            json_data = {'project': {'id_project': 1, 'devices': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only site admins can change things here")

            json_data = {'project': {'id_project': 1, 'devices': []}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(500, response.status_code, msg="Can't remove used devices by participants!")

            json_data = {'project': {'id_project': 2, 'devices': []}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Can't remove used devices by participants!")

            params = {'id_project': 2}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 0)  # Everything was deleted!

            json_data = {'project': {'id_project': 2, 'devices': [{'id_device': 1},
                                                                  {'id_device': 2},
                                                                  {'id_device': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="One device not allowed - not part of the site project!")

            json_data = {'project': {'id_project': 2, 'devices': [{'id_device': 1},
                                                                  {'id_device': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="New device association OK")

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 2)  # Everything was added

            json_data = {'project': {'id_project': 2, 'devices': [{'id_device': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove 1 device")
            self.assertIsNone(TeraDeviceProject.get_device_project_id_for_device_and_project(2, 2))
            self.assertIsNotNone(TeraDeviceProject.get_device_project_id_for_device_and_project(1, 2))

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            json_data = {'project': {'id_project': 2, 'devices': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Back to initial state")

    def test_post_device_project_and_delete(self):
        with self._flask_app.app_context():
            # Device-Project update
            json_data = {'device_project': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'device_project': {'id_project': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'device_project': {'id_project': 1, 'id_device': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only site admins can change things here")

            json_data = {'device_project': {'id_project': 1, 'id_device': 3}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Add new association not OK - device not part of the site")

            # Add device to site
            ds = TeraDeviceSite()
            ds.id_device = 3
            ds.id_site = 1
            ds = TeraDeviceSite.insert(ds)

            json_data = {'device_project': {'id_project': 1, 'id_device': 3}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add new association OK now")

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            json_data = response.json

            current_id = None
            for dp in json_data:
                if dp['id_device'] == 3:
                    current_id = dp['id_device_project']
                    break
            self.assertFalse(current_id is None)

            # Delete current association before adding it
            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(200, response.status_code, msg="Current association deleted")

            json_data = {'device_project': {'id_project': 1, 'id_device': 3}}
            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add new association OK")

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), TeraDeviceProject.get_count(filters={'id_project': 1}))

            current_id = None
            for dp in json_data:
                if dp['id_device'] == 3:
                    current_id = dp['id_device_project']
                    break
            self.assertFalse(current_id is None)
            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user', password='user',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params=params)
            self.assertEqual(200, response.status_code, msg="Delete OK")

            params = {'id_project': 1}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            json_data = response.json
            self.assertEqual(len(json_data), TeraDeviceProject.get_count(filters={'id_project': 1}))

            json_data = {'device': {'id_device': 3, 'projects': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Back to initial state")

            TeraDeviceSite.delete(ds.id_device_site)

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
