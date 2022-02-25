from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest


class UserQueryServiceSitesTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/services/sites'

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

    def test_query_site_as_admin(self):
        params = {'id_site': 10}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_site': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 3)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_site_with_services_as_admin(self):
        params = {'id_site': 1, 'with_services': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 6)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_service_as_admin(self):
        params = {'id_service': 30}  # Invalid service
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_service': 5}  # Videorehab service
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_service_with_site_as_admin(self):
        params = {'id_service': 3, 'with_sites': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_service_with_roles_as_admin(self):
        params = {'id_service': 3, 'with_roles': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)
            self.assertTrue(data_item.__contains__('service_roles'))

    def test_query_list_as_admin(self):
        params = {'id_site': 1, 'list': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 3)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_site_as_user(self):
        params = {'id_site': 10}
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_site': 1}
        response = self._request_with_http_auth(username='user4', password='user4', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_site': 1}
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_site_with_services_as_user(self):
        params = {'id_site': 1, 'with_services': 1}
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 3)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_service_as_user(self):
        params = {'id_service': 30}  # Invalid service
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_service': 3}  # File transfer service
        response = self._request_with_http_auth(username='user4', password='user4', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_service': 5}  # Videorehab service
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_service_with_sites_as_user(self):
        params = {'id_service': 5, 'with_sites': 1}  # Videorehab service
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        params = {'id_service': 5, 'list': 1}

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

    def test_post_service(self):
        # New with minimal infos
        json_data = {}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing everything")  # Missing

        # Service update
        json_data = {'service': {}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_service")

        json_data = {'service': {'id_service': 3}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing sites")

        json_data = {'service': {'id_service': 5, 'sites': []}}
        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Only super admins can change things here")

        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Nope, not site admin either!")

        json_data = {'service': {'id_service': 5, 'sites': []}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove from all projects OK")

        params = {'id_service': 5}  # Video rehab
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)  # Everything was deleted!

        json_data = {'service': {'id_service': 5, 'sites': [{'id_site': 1},
                                                            {'id_site': 2}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Add all sites OK")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)  # Everything was added

        json_data = {'service': {'id_service': 5, 'sites': [{'id_site': 1}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove one site")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        json_data = {'service': {'id_service': 5, 'sites': [{'id_site': 1},
                                                            {'id_site': 2}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Add all sites OK")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)  # Back to initial state

        # Recreate default associations - projects
        json_data = {'service': {'id_service': 3, 'projects': [{'id_project': 1},
                                                               {'id_project': 2},
                                                               {'id_project': 3}
                                                               ]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data,
                                             endpoint='/api/user/services/projects')
        self.assertEqual(response.status_code, 200)

        json_data = {'service': {'id_service': 5, 'projects': [{'id_project': 1}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data,
                                             endpoint='/api/user/services/projects')
        self.assertEqual(response.status_code, 200)

        # Recreate default associations - session types
        json_data = {'session_type_project': [{'id_session_type': 1, 'id_project': 1},
                                              {'id_session_type': 2, 'id_project': 1},
                                              {'id_session_type': 3, 'id_project': 1},
                                              {'id_session_type': 4, 'id_project': 1},
                                              {'id_session_type': 5, 'id_project': 1}]}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data,
                                             endpoint='/api/user/sessiontypeprojects')
        self.assertEqual(response.status_code, 200)

    def test_post_site(self):
        # Site update
        json_data = {'site': {}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_site")

        json_data = {'site': {'id_site': 1}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing services")

        json_data = {'site': {'id_site': 1, 'services': []}}
        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Only super admins can change things here")

        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Nope, not site admin either!")

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove all services OK")

        params = {'id_site': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)  # Everything was deleted!

        json_data = {'site': {'id_site': 1, 'services': [{'id_service': 2},
                                                         {'id_service': 3},
                                                         {'id_service': 4},
                                                         {'id_service': 5}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Add all services OK")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 4)  # Everything was added

        json_data = {'site': {'id_site': 1, 'services': [{'id_service': 2},
                                                         {'id_service': 3},
                                                         {'id_service': 5}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove 1 service")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 3)  # Back to the default state

        # Recreate default associations - projects
        json_data = {'service': {'id_service': 3, 'projects': [{'id_project': 1},
                                                               {'id_project': 2},
                                                               {'id_project': 3}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data,
                                             endpoint='/api/user/services/projects')
        self.assertEqual(response.status_code, 200)

        json_data = {'service': {'id_service': 5, 'projects': [{'id_project': 1}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data,
                                             endpoint='/api/user/services/projects')
        self.assertEqual(response.status_code, 200)

        # Recreate defaulta associations - session types
        json_data = {'session_type_project': [{'id_session_type': 1, 'id_project': 1},
                                              {'id_session_type': 2, 'id_project': 1},
                                              {'id_session_type': 3, 'id_project': 1},
                                              {'id_session_type': 4, 'id_project': 1},
                                              {'id_session_type': 5, 'id_project': 1}]}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data,
                                             endpoint='/api/user/sessiontypeprojects')
        self.assertEqual(response.status_code, 200)

    def test_post_service_site_and_delete(self):
        # Service-Project update
        json_data = {'service_site': {}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Badly formatted request")

        json_data = {'service_site': {'id_site': 1}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Badly formatted request")

        json_data = {'service_site': {'id_site': 1, 'id_service': 4}}
        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Only super admins can change things here")

        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Nope, not site admin either!")

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Add new association OK")

        params = {'id_site': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 4)

        current_id = None
        for sp in json_data:
            if sp['id_service'] == 4:
                current_id = sp['id_service_site']
                break
        self.assertFalse(current_id is None)

        response = self._delete_with_http_auth(username='user', password='user', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='siteadmin', password='siteadmin', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete still denied")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

        params = {'id_site': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 3)  # Back to initial state!

        # Recreate default associations - projects
        json_data = {'service': {'id_service': 3, 'projects': [{'id_project': 1},
                                                               {'id_project': 2},
                                                               {'id_project': 3}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data,
                                             endpoint='/api/user/services/projects')
        self.assertEqual(response.status_code, 200)

        json_data = {'service': {'id_service': 5, 'projects': [{'id_project': 1}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data,
                                             endpoint='/api/user/services/projects')
        self.assertEqual(response.status_code, 200)

        # Recreate defaulta associations - session types
        json_data = {'session_type_project': [{'id_session_type': 1, 'id_project': 1},
                                              {'id_session_type': 2, 'id_project': 1},
                                              {'id_session_type': 3, 'id_project': 1},
                                              {'id_session_type': 4, 'id_project': 1},
                                              {'id_session_type': 5, 'id_project': 1}]}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data,
                                             endpoint='/api/user/sessiontypeprojects')
        self.assertEqual(response.status_code, 200)

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_service_site'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('id_site'))

        if not minimal:
            self.assertTrue(json_data.__contains__('service_name'))
            self.assertTrue(json_data.__contains__('service_key'))
            self.assertTrue(json_data.__contains__('service_system'))
            self.assertTrue(json_data.__contains__('site_name'))
        else:
            self.assertFalse(json_data.__contains__('service_name'))
            self.assertFalse(json_data.__contains__('service_key'))
            self.assertFalse(json_data.__contains__('service_system'))
            self.assertFalse(json_data.__contains__('site_name'))
