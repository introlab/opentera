from BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite


class UserQuerySessionTypeSitesTest(BaseUserAPITest):
    test_endpoint = '/api/user/testtypes/sites'

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
            self.assertEqual(401, response.status_code)

    def test_delete_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.delete(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._get_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_post_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._post_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_http_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_http_auth(self.test_client, username='invalid', password='invalid')
            self.assertEqual(401, response.status_code)

    def test_delete_endpoint_invalid_token_auth(self):
        with self._flask_app.app_context():
            response = self._delete_with_user_token_auth(self.test_client, token='invalid')
            self.assertEqual(401, response.status_code)

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='admin', password='admin', client=self.test_client)
            self.assertEqual(response.status_code, 400)

    def test_query_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(username='user', password='user', params="",
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 400)

    def test_query_site_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 10}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_site': 2}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_site_with_test_types_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'with_test_types': 1}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 3)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_test_type_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 30}  # Invalid
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_test_type': 1}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_test_type_with_site_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 3, 'with_sites': 1}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'list': 1}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_site_as_user(self):
        with self._flask_app.app_context():
            params = {'id_site': 2}
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(username='user4', password='user4', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_site_with_test_types_as_user(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'with_test_types': 1}
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 2)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_test_type_as_user(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 30}  # Invalid
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_test_type': 4}
            response = self._get_with_user_http_auth(username='user4', password='user4', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            params = {'id_test_type': 2}
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_test_type_with_sites_as_user(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 1, 'with_sites': 1}
            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        with self._flask_app.app_context():
            params = {'id_test_type': 1, 'list': 1}

            response = self._get_with_user_http_auth(username='user4', password='user4', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 0)

            response = self._get_with_user_http_auth(username='user', password='user', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            for data_item in json_data:
                self._checkJson(json_data=data_item, minimal=True)

    def test_post_test_type(self):
        with self._flask_app.app_context():
            # Create test types and associate in the db for this test
            json_testtype = {
                'test_type_name': 'Test Type',
                'id_service': 1
            }
            testtype1 = TeraTestType()
            testtype1.from_json(json_testtype)
            TeraTestType.insert(testtype1)

            tts1 = TeraTestTypeSite()
            tts1.id_test_type = testtype1.id_test_type
            tts1.id_site = 1
            TeraTestTypeSite.insert(tts1)

            tts2 = TeraTestTypeSite()
            tts2.id_test_type = testtype1.id_test_type
            tts2.id_site = 2
            TeraTestTypeSite.insert(tts2)

            # New with minimal infos
            json_data = {}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing everything")  # Missing

            # Update
            json_data = {'test_type': {}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing id_test_type")

            json_data = {'test_type': {'id_test_type': testtype1.id_test_type}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing sites")

            json_data = {'test_type': {'id_test_type': testtype1.id_test_type, 'sites': []}}
            response = self._post_with_user_http_auth(username='user', password='user', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Remove from all accessible sites OK")

            params = {'id_test_type': testtype1.id_test_type}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)  # One should remain in the "top secret" site

            json_data = {'test_type': {'id_test_type': testtype1.id_test_type, 'sites': []}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Remove from all accessible sites OK")

            params = {'id_test_type': testtype1.id_test_type}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)  # None remaining now

            json_data = {'test_type': {'id_test_type': testtype1.id_test_type, 'sites': [{'id_site': 1},
                                                                                         {'id_site': 2}]}}
            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="No access to site 2")

            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="All posted ok")

            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 2)  # Everything was added

            json_data = {'test_type': {'id_test_type': testtype1.id_test_type, 'sites': [{'id_site': 1}]}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Remove one site")

            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            json_data = {'test_type': {'id_test_type': testtype1.id_test_type, 'sites': [{'id_site': 1},
                                                                                         {'id_site': 2}]}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Add all sites OK")

            TeraTestType.delete(testtype1.id_test_type)

    def test_post_site(self):
        with self._flask_app.app_context():
            # Create test types and associate in the db for this test
            json_testtype = {
                'test_type_name': 'Test Type',
                'id_service': 1
            }
            testtype1 = TeraTestType()
            testtype1.from_json(json_testtype)
            TeraTestType.insert(testtype1)

            testtype2 = TeraTestType()
            testtype2.from_json(json_testtype)
            TeraTestType.insert(testtype2)

            tts1 = TeraTestTypeSite()
            tts1.id_test_type = testtype1.id_test_type
            tts1.id_site = 2
            TeraTestTypeSite.insert(tts1)

            tts2 = TeraTestTypeSite()
            tts2.id_test_type = testtype2.id_test_type
            tts2.id_site = 2
            TeraTestTypeSite.insert(tts2)

            # Site update
            json_data = {'site': {}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing id_site")

            json_data = {'site': {'id_site': 2}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Missing services")

            json_data = {'site': {'id_site': 2, 'testtypes': []}}
            response = self._post_with_user_http_auth(username='user', password='user', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Remove all test types OK")

            params = {'id_site': 2}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 0)  # Everything was deleted!

            json_data = {'site': {'id_site': 2, 'testtypes': [{'id_test_type': testtype1.id_test_type},
                                                              {'id_test_type': testtype2.id_test_type}
                                                              ]}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Add all test types OK")

            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 2)  # Everything was added

            json_data = {'site': {'id_site': 2, 'testtypes': [{'id_test_type': testtype2.id_test_type}]}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Remove 1 test type")

            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 1)

            json_data = {'site': {'id_site': 2, 'testtypes': [{'id_test_type': 1},
                                                              {'id_test_type': 2},
                                                              {'id_test_type': 3}
                                                              ]}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Back to defaults")

            # Delete all created for that test
            TeraTestType.delete(testtype1.id_test_type)
            TeraTestType.delete(testtype2.id_test_type)

    def test_post_test_type_site_and_delete(self):
        with self._flask_app.app_context():
            json_data = {'test_type_site': {}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Badly formatted request")

            json_data = {'test_type_site': {'id_site': 2}}
            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 400, msg="Badly formatted request")

            json_data = {'test_type_site': {'id_site': 2, 'id_test_type': 2}}
            response = self._post_with_user_http_auth(username='user', password='user', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Only site admins can change things here")

            response = self._post_with_user_http_auth(username='siteadmin', password='siteadmin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Not site admin either for that site")

            response = self._post_with_user_http_auth(username='admin', password='admin', json=json_data,
                                                      client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Add new association OK")

            params = {'id_site': 2}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            target_count = len(TeraTestTypeSite.get_tests_types_for_site(2))
            self.assertEqual(len(json_data), target_count)

            current_id = None
            for sp in json_data:
                if sp['id_test_type'] == 2:
                    current_id = sp['id_test_type_site']
                    break
            self.assertFalse(current_id is None)

            response = self._delete_with_user_http_auth(username='user', password='user',
                                                        params='id=' + str(current_id),
                                                        client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Delete denied")

            response = self._delete_with_user_http_auth(username='siteadmin', password='siteadmin',
                                                        params='id=' + str(current_id), client=self.test_client)
            self.assertEqual(response.status_code, 403, msg="Delete still denied")

            response = self._delete_with_user_http_auth(username='admin', password='admin',
                                                        params='id=' + str(current_id), client=self.test_client)
            self.assertEqual(response.status_code, 200, msg="Delete OK")

            params = {'id_site': 2}
            response = self._get_with_user_http_auth(username='admin', password='admin', params=params,
                                                     client=self.test_client)
            self.assertEqual(response.status_code, 200)
            json_data = response.json
            self.assertEqual(len(json_data), 2)  # Back to initial state!

    def _checkJson(self, json_data, minimal=False):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_test_type_site'))
        self.assertTrue(json_data.__contains__('id_test_type'))
        self.assertTrue(json_data.__contains__('id_site'))

        if not minimal:
            self.assertTrue(json_data.__contains__('test_type_name'))
            self.assertTrue(json_data.__contains__('site_name'))
        else:
            self.assertFalse(json_data.__contains__('test_type_name'))
            self.assertFalse(json_data.__contains__('site_name'))
