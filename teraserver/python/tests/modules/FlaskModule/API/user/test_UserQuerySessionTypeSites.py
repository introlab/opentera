from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest


class UserQuerySessionTypeSitesTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/sessiontypes/sites'

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

        params = {'id_site': 2}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_site_with_session_types_as_admin(self):
        params = {'id_site': 1, 'with_session_type': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 5)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_session_type_as_admin(self):
        params = {'id_session_type': 30}  # Invalid
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_session_type': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_session_type_with_site_as_admin(self):
        params = {'id_session_type': 3, 'with_sites': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_list_as_admin(self):
        params = {'id_site': 1, 'list': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 5)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_site_as_user(self):
        params = {'id_site': 2}
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
        self.assertEqual(len(json_data), 5)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_site_with_session_types_as_user(self):
        params = {'id_site': 1, 'with_session_type': 1}
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 5)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_session_type_as_user(self):
        params = {'id_session_type': 30}  # Invalid
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_session_type': 4}
        response = self._request_with_http_auth(username='user4', password='user4', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        params = {'id_session_type': 2}
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_session_type_with_sites_as_user(self):
        params = {'id_session_type': 1, 'with_sites': 1}
        response = self._request_with_http_auth(username='user', password='user', payload=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        params = {'id_session_type': 1, 'list': 1}

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

    def test_post_session_type(self):
        # New with minimal infos
        json_data = {}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing everything")  # Missing

        # Update
        json_data = {'session_type': {}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_session_type")

        json_data = {'session_type': {'id_session_type': 1}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing sites")

        json_data = {'session_type': {'id_session_type': 1, 'sites': []}}
        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove from all accessible sites OK")

        params = {'id_session_type': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)  # One should remain in the "top secret" site

        json_data = {'session_type': {'id_session_type': 1, 'sites': []}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove from all accessible sites OK")

        params = {'id_session_type': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)  # None remaining now

        json_data = {'session_type': {'id_session_type': 1, 'sites': [{'id_site': 1},
                                                                      {'id_site': 2}]}}
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="No access to site 2")

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="All posted ok")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)  # Everything was added

        json_data = {'session_type': {'id_session_type': 1, 'sites': [{'id_site': 1}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove one site")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        json_data = {'session_type': {'id_session_type': 1, 'sites': [{'id_site': 1},
                                                                      {'id_site': 2}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Add all sites OK")

        # Recreate default associations - projects
        json_data = {'session_type_project': [{'id_session_type': 1, 'id_project': 1}]}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data,
                                             endpoint='/api/user/sessiontypes/projects')
        self.assertEqual(response.status_code, 200)

    def test_post_site(self):
        # Site update
        json_data = {'site': {}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_site")

        json_data = {'site': {'id_site': 1}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing services")

        json_data = {'site': {'id_site': 1, 'sessiontypes': []}}
        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove all services OK")

        params = {'id_site': 1}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 0)  # Everything was deleted!

        json_data = {'site': {'id_site': 1, 'sessiontypes': [{'id_session_type': 1},
                                                             {'id_session_type': 2}
                                                            ]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Add all session types OK")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)  # Everything was added

        json_data = {'site': {'id_site': 1, 'sessiontypes': [{'id_session_type': 2}]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Remove 1 session type")

        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        json_data = {'site': {'id_site': 1, 'sessiontypes': [{'id_session_type': 1},
                                                             {'id_session_type': 2},
                                                             {'id_session_type': 3},
                                                             {'id_session_type': 4},
                                                             {'id_session_type': 5}
                                                             ]}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Back to defaults")

        # Recreate default associations - projects
        json_data = {'session_type_project': [{'id_session_type': 1, 'id_project': 1},
                                              {'id_session_type': 2, 'id_project': 1},
                                              {'id_session_type': 3, 'id_project': 1},
                                              {'id_session_type': 4, 'id_project': 1},
                                              {'id_session_type': 5, 'id_project': 1}]}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data,
                                             endpoint='/api/user/sessiontypes/projects')
        self.assertEqual(response.status_code, 200)

    def test_post_session_type_site_and_delete(self):
        json_data = {'session_type_site': {}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Badly formatted request")

        json_data = {'session_type_site': {'id_site': 2}}
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Badly formatted request")

        json_data = {'session_type_site': {'id_site': 2, 'id_session_type': 3}}
        response = self._post_with_http_auth(username='user', password='user', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Not site admin either for that site")

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Add new association OK")

        params = {'id_site': 2}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

        current_id = None
        for sp in json_data:
            if sp['id_session_type'] == 3:
                current_id = sp['id_session_type_site']
                break
        self.assertFalse(current_id is None)

        response = self._delete_with_http_auth(username='user', password='user', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='siteadmin', password='siteadmin', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete still denied")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

        params = {'id_site': 2}
        response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)  # Back to initial state!

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_session_type'))
        self.assertTrue(json_data.__contains__('id_session_type'))
        self.assertTrue(json_data.__contains__('id_site'))

        if not minimal:
            self.assertTrue(json_data.__contains__('session_type_name'))
            self.assertTrue(json_data.__contains__('site_name'))
        else:
            self.assertFalse(json_data.__contains__('session_type_name'))
            self.assertFalse(json_data.__contains__('site_name'))
