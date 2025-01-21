from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraService import TeraService


class UserQueryServiceSitesTest(BaseUserAPITest):
    test_endpoint = '/api/user/services/sites'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_no_auth(self):
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
        response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin')
        self.assertEqual(400, response.status_code)

    def test_query_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client,  username='user', password='user')
            self.assertEqual(400, response.status_code)

    def test_query_site_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 10}
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = len(TeraServiceSite.get_services_for_site(1))
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_site_with_services_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'with_services': 1}
            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = TeraService.get_count() - 1  # Ignore OpenTeraService
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_service_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_service': 30}  # Invalid service
            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            service: TeraService = TeraService.get_service_by_key('VideoRehabService')
            params = {'id_service': service.id_service}  # Videorehab service
            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_service_with_site_as_admin(self):
        with self._flask_app.app_context():
            service: TeraService = TeraService.get_service_by_key('FileTransferService')
            params = {'id_service': service.id_service, 'with_sites': 1}
            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(2, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_service_with_roles_as_admin(self):
        with self._flask_app.app_context():
            service: TeraService = TeraService.get_service_by_key('FileTransferService')
            params = {'id_service': service.id_service, 'with_roles': 1}
            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = len(TeraServiceSite.get_sites_for_service(3))
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertTrue(data_item.__contains__('service_roles'))

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'list': 1}
            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = len(TeraServiceSite.get_services_for_site(1))
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_site_as_user(self):
        with self._flask_app.app_context():
            params = {'id_site': 10}
            response = self._get_with_user_http_auth(self.test_client,  username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(self.test_client,  username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(self.test_client,  username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = TeraServiceSite.get_count(filters={'id_site': 1})
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_site_with_services_as_user(self):
        with self._flask_app.app_context():
            params = {'id_site': 1, 'with_services': 1}
            response = self._get_with_user_http_auth(self.test_client,  username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            target_count = TeraServiceSite.get_count(filters={'id_site': 1})
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_service_as_user(self):
        with self._flask_app.app_context():
            params = {'id_service': 30}  # Invalid service
            response = self._get_with_user_http_auth(self.test_client,  username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            service: TeraService = TeraService.get_service_by_key('FileTransferService')
            params = {'id_service': service.id_service}  # File transfer service
            response = self._get_with_user_http_auth(self.test_client,  username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            service: TeraService = TeraService.get_service_by_key('VideoRehabService')
            params = {'id_service': service.id_service}  # Videorehab service
            response = self._get_with_user_http_auth(self.test_client,  username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_service_with_sites_as_user(self):
        with self._flask_app.app_context():
            service: TeraService = TeraService.get_service_by_key('VideoRehabService')
            params = {'id_service': service.id_service, 'with_sites': 1}  # Videorehab service
            response = self._get_with_user_http_auth(self.test_client,  username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_list_as_user(self):
        with self._flask_app.app_context():
            service: TeraService = TeraService.get_service_by_key('VideoRehabService')
            params = {'id_service': service.id_service, 'list': 1}

            response = self._get_with_user_http_auth(self.test_client,  username='user4', password='user4',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(0, len(response.json))

            response = self._get_with_user_http_auth(self.test_client,  username='user', password='user',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(1, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_post_service(self):
        with self._flask_app.app_context():
            # New with minimal infos
            json_data = {}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing everything")  # Missing

            # Service update
            json_data = {'service': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_service")

            file_service: TeraService = TeraService.get_service_by_key('FileTransferService')
            bureau_service: TeraService = TeraService.get_service_by_key('BureauActif')
            video_service: TeraService = TeraService.get_service_by_key('VideoRehabService')
            json_data = {'service': {'id_service': file_service.id_service}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing sites")

            json_data = {'service': {'id_service': bureau_service.id_service, 'sites': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only super admins can change things here")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Nope, not site admin either!")

            json_data = {'service': {'id_service': video_service.id_service, 'sites': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(500, response.status_code, msg="Can't remove - has sessions types with sessions")

            json_data = {'service': {'id_service': bureau_service.id_service, 'sites': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove from all projects OK")

            params = {'id_service': bureau_service.id_service}
            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            json_data = {'service': {'id_service': bureau_service.id_service,
                                     'sites': [{'id_site': 1},
                                               {'id_site': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all sites OK")

            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))  # Everything was added

            json_data = {'service': {'id_service': bureau_service.id_service, 'sites': [{'id_site': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove one site")
            self.assertIsNone(TeraServiceSite.get_service_site_for_service_site(site_id=2,
                                                                                service_id=bureau_service.id_service))
            self.assertIsNotNone(TeraServiceSite.get_service_site_for_service_site(site_id=1,
                                                                                   service_id=bureau_service.id_service))

            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))

            json_data = {'service': {'id_service': bureau_service.id_service,
                                     'sites': [{'id_site': 1},
                                               {'id_site': 2}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all sites OK")

            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2, len(response.json))  # Back to initial state

            json_data = {'service': {'id_service': bureau_service.id_service, 'sites': [{'id_site': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Back to initial sites OK")

            # Recreate default associations - projects
            json_data = {'service': {'id_service': file_service.id_service,
                                     'projects': [{'id_project': 1},
                                                  {'id_project': 2},
                                                  {'id_project': 3}
                                                 ]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data,
                                                      endpoint='/api/user/services/projects')
            self.assertEqual(200, response.status_code)

            json_data = {'service': {'id_service': video_service.id_service, 'projects': [{'id_project': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data,
                                                      endpoint='/api/user/services/projects')
            self.assertEqual(200, response.status_code)

            # Recreate default associations - session types
            json_data = {'site': {'id_site': 1, 'sessiontypes': [{'id_session_type': 1},
                                                                 {'id_session_type': 2},
                                                                 {'id_session_type': 3},
                                                                 {'id_session_type': 4},
                                                                 {'id_session_type': 5}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data,
                                                      endpoint='/api/user/sessiontypes/sites')
            self.assertEqual(200, response.status_code)

            json_data = {'session_type_project': [{'id_session_type': 1, 'id_project': 1},
                                                  {'id_session_type': 2, 'id_project': 1},
                                                  {'id_session_type': 3, 'id_project': 1},
                                                  {'id_session_type': 4, 'id_project': 1},
                                                  {'id_session_type': 5, 'id_project': 1}]}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data,
                                                      endpoint='/api/user/sessiontypes/projects')
            self.assertEqual(200, response.status_code)

    def test_post_site(self):
        with self._flask_app.app_context():
            # Site update
            json_data = {'site': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing id_site")

            json_data = {'site': {'id_site': 2}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing services")

            json_data = {'site': {'id_site': 2, 'services': []}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only super admins can change things here")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Nope, not site admin either!")

            json_data = {'site': {'id_site': 1, 'services': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(500, response.status_code, msg="Sessions with sessions type with that service")

            json_data = {'site': {'id_site': 2, 'services': []}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove all services OK")

            params = {'id_site': 2}
            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))  # Everything was deleted!

            logging_service: TeraService = TeraService.get_service_by_key('LoggingService')
            file_service: TeraService = TeraService.get_service_by_key('FileTransferService')
            bureau_service: TeraService = TeraService.get_service_by_key('BureauActif')
            video_service: TeraService = TeraService.get_service_by_key('VideoRehabService')
            json_data = {'site': {'id_site': 2,
                                  'services': [{'id_service': logging_service.id_service},
                                               {'id_service': file_service.id_service},
                                               {'id_service': bureau_service.id_service},
                                               {'id_service': video_service.id_service}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add all services OK")

            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(4, len(response.json))  # Everything was added

            json_data = {'site': {'id_site': 2, 'services': [{'id_service': file_service.id_service}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Remove 1 service")
            self.assertIsNotNone(TeraServiceSite.get_service_site_for_service_site(site_id=2,
                                                                                   service_id=file_service.id_service))
            self.assertIsNone(TeraServiceSite.get_service_site_for_service_site(site_id=2,
                                                                                service_id=bureau_service.id_service))
            self.assertIsNone(TeraServiceSite.get_service_site_for_service_site(site_id=2,
                                                                                service_id=logging_service.id_service))
            self.assertIsNone(TeraServiceSite.get_service_site_for_service_site(site_id=2,
                                                                                service_id=video_service.id_service))

            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.json))  # Back to the default state

    def test_post_service_site_and_delete(self):
        with self._flask_app.app_context():
            # Service-Project update
            json_data = {'service_site': {}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            json_data = {'service_site': {'id_site': 1}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Badly formatted request")

            service: TeraService = TeraService.get_service_by_key('BureauActif')
            json_data = {'service_site': {'id_site': 1, 'id_service': service.id_service}}
            response = self._post_with_user_http_auth(self.test_client, username='user', password='user',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Only super admins can change things here")

            response = self._post_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Nope, not site admin either!")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Add new association OK")

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin', params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(4, len(response.json))

            current_id = None
            for sp in response.json:
                if sp['id_service'] == service.id_service:
                    current_id = sp['id_service_site']
                    break
            self.assertFalse(current_id is None)

            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user', password='user',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            response = self._delete_with_user_http_auth(self.test_client, username='siteadmin', password='siteadmin',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete still denied")

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(200, response.status_code, msg="Delete OK")

            params = {'id_site': 1}
            response = self._get_with_user_http_auth(self.test_client,  username='admin', password='admin', params=params)
            self.assertEqual(200, response.status_code)
            self.assertEqual(3, len(response.json))  # Back to initial state!

            # Recreate default associations - projects
            service: TeraService = TeraService.get_service_by_key('FileTransferService')
            json_data = {'service': {'id_service': service.id_service,
                                     'projects': [{'id_project': 1},
                                                  {'id_project': 2},
                                                  {'id_project': 3}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data,
                                                      endpoint='/api/user/services/projects')
            self.assertEqual(200, response.status_code)

            service: TeraService = TeraService.get_service_by_key('VideoRehabService')
            json_data = {'service': {'id_service': service.id_service, 'projects': [{'id_project': 1}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data,
                                                      endpoint='/api/user/services/projects')
            self.assertEqual(200, response.status_code)

            # Recreate defaults associations - session types
            json_data = {'site': {'id_site': 1, 'sessiontypes': [{'id_session_type': 1},
                                                                 {'id_session_type': 2},
                                                                 {'id_session_type': 3},
                                                                 {'id_session_type': 4},
                                                                 {'id_session_type': 5}]}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=json_data,
                                                      endpoint='/api/user/sessiontypes/sites')
            self.assertEqual(200, response.status_code)

            json_data = {'session_type_project': [{'id_session_type': 1, 'id_project': 1},
                                                  {'id_session_type': 2, 'id_project': 1},
                                                  {'id_session_type': 3, 'id_project': 1},
                                                  {'id_session_type': 4, 'id_project': 1},
                                                  {'id_session_type': 5, 'id_project': 1}]}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=json_data,
                                                      endpoint='/api/user/sessiontypes/projects')
            self.assertEqual(200, response.status_code)

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
