from tests.modules.FlaskModule.API.BaseAPITest import BaseAPITest


class UserQuerySessionTypesTest(BaseAPITest):
    login_endpoint = '/api/user/login'
    test_endpoint = '/api/user/sessiontypes'

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
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        for data_item in json_data:
            self.assertGreater(len(data_item), 0)
            self.assertTrue(data_item.__contains__('id_session_type'))
            self.assertTrue(data_item.__contains__('session_type_category'))
            self.assertTrue(data_item.__contains__('session_type_config'))
            self.assertTrue(data_item.__contains__('session_type_name'))
            self.assertTrue(data_item.__contains__('session_type_online'))
            self.assertTrue(data_item.__contains__('session_type_color'))

    def test_query_list_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="list=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertGreater(len(json_data), 0)

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_session_type=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 1)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

    def test_query_specific_project_as_admin(self):
        response = self._request_with_http_auth(username='admin', password='admin', payload="id_project=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()
        self.assertEqual(len(json_data), 0)

        for data_item in json_data:
            self._checkJson(json_data=data_item)

        response = self._request_with_http_auth(username='admin', password='admin', payload="id_project=1&list=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        json_data = response.json()

        for data_item in json_data:
            self._checkJson(json_data=data_item, minimal=True)

    def test_post_and_delete(self):
        # New with minimal infos
        json_data = {
            'session_type': {
                'id_service': None,
                'session_type_category': 1,
                'session_type_color': 'red',
                'session_type_name': 'Test',
                'session_type_online': True
            }
        }

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_session_type")  # Missing id_session_type

        json_data['session_type']['id_session_type'] = 0
        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 400, msg="Missing id_service")  # Missing id_service

        json_data['session_type']['id_service'] = 1
        json_data['session_type']['session_type_projects'] = [{'id_project': 1}, {'id_project': 3}]
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="No access to project!")

        response = self._post_with_http_auth(username='user4', password='user4', payload=json_data)
        self.assertEqual(response.status_code, 403, msg="Post denied for user")  # Forbidden for that user to post that

        response = self._post_with_http_auth(username='admin', password='admin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post new")  # All ok now!

        json_data = response.json()[0]
        self._checkJson(json_data)
        current_id = json_data['id_session_type']

        json_data = {
            'session_type': {
                'id_session_type': current_id,
                'session_type_category': 2,
                'session_type_name': 'Test 2',
                'session_type_projects': [{'id_project': 1}, {'id_project': 2}]
            }
        }

        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Post update")
        reply_data = response.json()[0]
        self._checkJson(reply_data)
        self.assertEqual(reply_data['session_type_name'], 'Test 2')
        self.assertEqual(reply_data['session_type_category'], 2)

        # Check that the untouched project is still there
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_session_type=" + str(current_id),
                                                endpoint='/api/user/sessiontypeprojects')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        reply_data = response.json()
        self.assertEqual(len(reply_data), 3)

        json_data['session_type']['session_type_projects'] = [{'id_project': 1}]
        response = self._post_with_http_auth(username='siteadmin', password='siteadmin', payload=json_data)
        self.assertEqual(response.status_code, 200, msg="Changed user groups")

        # Check that the untouched project is still there
        response = self._request_with_http_auth(username='admin', password='admin',
                                                payload="id_session_type=" + str(current_id),
                                                endpoint='/api/user/sessiontypeprojects')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        reply_data = response.json()
        self.assertEqual(len(reply_data), 2)

        response = self._delete_with_http_auth(username='user4', password='user4', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Delete denied")

        response = self._delete_with_http_auth(username='siteadmin', password='siteadmin', id_to_del=current_id)
        self.assertEqual(response.status_code, 403, msg="Can't delete because not admin on all projects")

        response = self._delete_with_http_auth(username='admin', password='admin', id_to_del=current_id)
        self.assertEqual(response.status_code, 200, msg="Delete OK")

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_session_type'))
        self.assertTrue(json_data.__contains__('id_service'))
        self.assertTrue(json_data.__contains__('session_type_category'))
        self.assertTrue(json_data.__contains__('session_type_name'))
        if not minimal:
            self.assertTrue(json_data.__contains__('session_type_config'))
            self.assertTrue(json_data.__contains__('session_type_online'))
            self.assertTrue(json_data.__contains__('session_type_color'))

