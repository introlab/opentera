from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraService import TeraService
import datetime


class UserQueryServicesTest(BaseUserAPITest):
    test_endpoint = '/api/user/services'

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
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(200, response.status_code)
            target_count = TeraService.get_count() - 1  # Never returns OpenTera service
            self.assertEqual(target_count, len(response.json))

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_as_user(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='user', password='user')
            self.assertGreater(len(response.json), 0)

    def test_query_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                # Logger service should not be here since a system service!
                # self.assertNotEqual(data_item['id_service'], 2)
                # ... but not allowed when requesting as superadmin!

    def test_query_list_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertGreater(len(response.json), 0)

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_query_specific_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            # OpenTera service is a system service, and should not be returned here!
            self.assertEqual(len(response.json), 0)

            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_service': 4})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 1)

            service_uuid = None
            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_service'], 4)
                service_uuid = data_item['service_uuid']

            # Now try to query with service uuid
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'uuid': service_uuid})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['id_service'], 4)
                self.assertEqual(data_item['service_uuid'], service_uuid)

    def test_query_services_for_project_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_project': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 2)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_services_for_site_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'id_site': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 3)

            for data_item in response.json:
                self._checkJson(json_data=data_item)

    def test_query_by_key_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'key': 'VideoRehabService'})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            self.assertEqual(len(response.json), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item)
                self.assertEqual(data_item['service_key'], 'VideoRehabService')

    def test_query_with_config_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params={'with_config': 1, 'list': 1})
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.is_json)
            json_data = response.json
            self.assertGreaterEqual(len(json_data), 1)

            for data_item in response.json:
                self._checkJson(json_data=data_item, minimal=True)

    def test_post_and_delete(self):
        with self._flask_app.app_context():
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

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(response.status_code, 400, msg="Missing id_service")  # Missing id_service

            json_data['service']['id_service'] = 0
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(400, response.status_code, msg="Missing service_key")

            json_data['service']['service_key'] = 'Test'
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            # json=json_data)
            # self.assertEqual(response.status_code, 400, msg="Invalid insert service_config_schema")

            del json_data['service']['service_config_schema']  # Will use default value
            response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                      json=json_data)
            self.assertEqual(403, response.status_code, msg="Post denied for user")

            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post new")  # All ok now!

            json_data = response.json[0]
            self._checkJson(json_data)
            current_id = json_data['id_service']
            current_uuid = json_data['service_uuid']

            json_data = {
                'service': {
                    'id_service': current_id,
                    'service_enabled': False,
                    'service_system': False,
                    'service_name': 'Test2',
                    'service_key': 'service_key',
                    'service_config_schema': '{Test'
                }
            }
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            # json=json_data)
            # self.assertEqual(403, response.status_code, msg="Post update with service_system that shouldn't be here")

            # del json_data['service']['service_system']
            # response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
            # json=json_data)
            # self.assertEqual(response.status_code, 400, msg="Post update with invalid config schema")

            del json_data['service']['service_config_schema']
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                      json=json_data)
            self.assertEqual(200, response.status_code, msg="Post update OK")
            json_data = response.json[0]
            self._checkJson(json_data)
            self.assertEqual(json_data['service_enabled'], False)
            self.assertEqual(json_data['service_name'], 'Test2')

            # Check that default service roles (admin, user) were created
            # self.assertTrue(json_data.__contains__('service_roles'))
            # self.assertEqual(len(json_data['service_roles']), 2)
            # self.assertEqual(json_data['service_roles'][0]['service_role_name'], 'admin')
            # self.assertEqual(json_data['service_roles'][1]['service_role_name'], 'user')

            params = {'id': current_id}
            response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                        params=params)
            self.assertEqual(403, response.status_code, msg="Delete denied")

            # Create a session of that service
            participant = TeraParticipant.get_participant_by_id(4)  # Participant in Secret Site
            site: TeraSite = TeraSite.get_site_by_id(2)
            project = site.site_projects[0]

            ss = TeraServiceSite()
            ss.id_site = site.id_site
            ss.id_service = current_id
            TeraServiceSite.insert(ss)

            sp = TeraServiceProject()
            sp.id_project = project.id_project
            sp.id_service = current_id
            TeraServiceProject.insert(sp)

            st = TeraSessionType()
            st.id_service = current_id
            st.session_type_category = 1
            st.session_type_online = True
            st.session_type_name = 'Test Session Type'
            st.session_type_color = 'black'
            TeraSessionType.insert(st)

            sts = TeraSessionTypeSite()
            sts.id_site = site.id_site
            sts.id_session_type = st.id_session_type
            TeraSessionTypeSite.insert(sts)

            stp1 = TeraSessionTypeProject()
            stp1.id_project = project.id_project
            stp1.id_session_type = st.id_session_type
            TeraSessionTypeProject.insert(stp1)

            tt = TeraTestType()
            tt.id_service = current_id
            tt.test_type_name = 'Test Type Test'
            tt.test_type_key = 'TEST'
            tt.test_type_has_web_format = False
            tt.test_type_has_json_format = False
            tt.test_type_has_web_editor = False
            TeraTestType.insert(tt)

            tts = TeraTestTypeSite()
            tts.id_test_type = tt.id_test_type
            tts.id_site = site.id_site
            TeraTestTypeSite.insert(tts)

            ttp = TeraTestTypeProject()
            ttp.id_project = project.id_project
            ttp.id_test_type = tt.id_test_type
            TeraTestTypeProject.insert(ttp)

            json_session = {'id_session_type': st.id_session_type,
                            'session_name': 'Session of session type',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            'id_creator_participant': participant.id_participant
                            }
            session1 = TeraSession()
            session1.from_json(json_session)
            TeraSession.insert(session1)

            json_test = {'id_test_type': tt.id_test_type,
                         'id_session': session1.id_session,
                         'test_name': 'Test Test',
                         'test_datetime': datetime.datetime.now()
                         }
            test = TeraTest()
            test.from_json(json_test)
            TeraTest.insert(test)

            json_asset = {'id_session': session1.id_session,
                          'asset_name': "Test asset",
                          'asset_service_uuid': current_uuid,
                          'asset_type': "Test",
                          'test_datetime': datetime.datetime.now()
                          }
            asset = TeraAsset()
            asset.from_json(json_asset)
            TeraAsset.insert(asset)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(500, response.status_code, msg="Can't delete: assets")
            TeraAsset.delete(asset.id_asset)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(500, response.status_code, msg="Can't delete: tests")
            TeraTest.delete(test.id_test)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(500, response.status_code, msg="Can't delete: sessions")
            TeraSession.delete(session1.id_session)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params=params)
            self.assertEqual(200, response.status_code, msg="Delete OK")

            TeraTestType.delete(tt.id_test_type)
            TeraSessionType.delete(st.id_session_type)

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
            self.assertTrue(json_data.__contains__('service_projects'))
            # self.assertTrue(json_data.__contains__('service_editable_config'))
        else:
            self.assertFalse(json_data.__contains__('service_roles'))
            self.assertFalse(json_data.__contains__('service_projects'))
            # self.assertFalse(json_data.__contains__('service_editable_config'))
