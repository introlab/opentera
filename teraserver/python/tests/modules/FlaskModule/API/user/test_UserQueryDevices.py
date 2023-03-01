from tests.modules.FlaskModule.API.user.BaseUserAPITest import BaseUserAPITest
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionDevices import TeraSessionDevices
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraService import TeraService

import datetime


class UserQueryDevicesTest(BaseUserAPITest):
    test_endpoint = '/api/user/devices'

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
            self.assertEqual(response.status_code, 401)

    def test_query_no_params_as_admin(self):
        with self._flask_app.app_context():
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
            self.assertEqual(response.status_code, 200)

    def _checkJson(self, json_data, params):
        for js in json_data:
            self.assertGreater(len(json_data), 0)
            self.assertTrue(js.__contains__('device_enabled'))
            self.assertTrue(js.__contains__('device_name'))
            self.assertTrue(js.__contains__('device_uuid'))
            self.assertTrue(js.__contains__('id_device'))
            self.assertTrue(js.__contains__('id_device_subtype'))
            self.assertTrue(js.__contains__('id_device_type'))

            if params['projects']:
                self.assertTrue(js.__contains__('device_projects'))
                for dp in js['device_projects']:
                    self.assertTrue(dp.__contains__('id_device'))
                    self.assertTrue(dp.__contains__('id_device_project'))
                    self.assertTrue(dp.__contains__('id_project'))

            if not params['list']:
                self.assertTrue(js.__contains__('device_config'))
                self.assertTrue(js.__contains__('device_infos'))
                self.assertTrue(js.__contains__('device_lastonline'))
                self.assertTrue(js.__contains__('device_notes'))
                self.assertTrue(js.__contains__('device_onlineable'))
                self.assertTrue(js.__contains__('device_token'))

            if params['with_participants']:
                self.assertTrue(js.__contains__('device_participants'))
                for awp in js['device_participants']:
                    self.assertTrue(awp.__contains__('id_participant'))
                    self.assertTrue(awp.__contains__('id_project'))
                    self.assertTrue(awp.__contains__('participant_name'))

            if params['with_sites']:
                self.assertTrue(js.__contains__('device_sites'))
                for aws in js['device_sites']:
                    self.assertTrue(aws.__contains__('id_site'))

            if params['with_status']:
                self.assertTrue(js.__contains__('device_busy'))
                self.assertTrue(js.__contains__('device_enabled'))

    def _checkJsonPost(self, json_data):
        for js in json_data:
            self.assertGreater(len(json_data), 0)
            self.assertTrue(js.__contains__('device_config'))
            self.assertTrue(js.__contains__('device_enabled'))
            self.assertTrue(js.__contains__('device_lastonline'))
            self.assertTrue(js.__contains__('device_name'))
            self.assertTrue(js.__contains__('device_notes'))
            self.assertTrue(js.__contains__('device_onlineable'))
            self.assertTrue(js.__contains__('device_token'))
            self.assertTrue(js.__contains__('device_uuid'))
            self.assertTrue(js.__contains__('id_device'))
            self.assertTrue(js.__contains__('id_device_subtype'))
            self.assertTrue(js.__contains__('id_device_type'))

    def test_query_get_as_admin(self):
        # # Get all the devices
        params = {'projects': 1, 'enabled': 1, 'list': 1, 'with_participants': 1,
                  'with_sites': 1, 'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self._checkJson(json_data=response.json, params=params)
        #
        params = {'id_device': 0, 'projects': 0, 'enabled': 1, 'list': 1,
                  'with_participants': 1, 'with_sites': 1, 'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)
        #
        params = {'id_device': 1, 'projects': 1, 'enabled': 0, 'list': 1,
                  'with_participants': 1, 'with_sites': 1, 'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self._checkJson(json_data=response.json, params=params)
        #
        params = {'id_device': 100, 'projects': 1, 'enabled': 1, 'list': 0,
                  'with_participants': 1, 'with_sites': 1, 'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        #
        params = {'id_device': 1, "device_uuid": "b707e0b2-e649-47e7-a938-2b949c423f73", 'projects': 1,
                  'enabled': 1, 'list': 1, 'with_participants': 0, 'with_sites': 1,
                  'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 400)

        params = {"device_uuid": "b707e0b2-e649-47e7-a938-2b949c423f73", 'projects': 1,
                  'enabled': 1, 'list': 1, 'with_participants': 1, 'with_sites': 1,
                  'with_status': 0}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self._checkJson(json_data=response.json, params=params)
        #
        params = {"uuid": "b707e0b2-e649-47e7-a938-2b949c423f73", 'projects': 1,
                  'enabled': 0, 'list': 1, 'with_participants': 0, 'with_sites': 1,
                  'with_status': 0}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self._checkJson(json_data=response.json, params=params)

        # There is an error in the uuid
        params = {"uuid": "b707e0b2-e649-47e7-a938-2b949e423f73", 'projects': 0,
                  'enabled': 1, 'list': 0, 'with_participants': 1, 'with_sites': 0,
                  'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        params = {"device_uuid": "b707e0b2-e649-47e7-a938-2b949c423f73", "uuid": "b707e0b2-e649-47e7-a938-2b949e423f73",
                  'projects': 1, 'enabled': 1, 'list': 1, 'with_participants': 0,
                  'with_sites': 0, 'with_status': 0}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 400)

        params = {'id_site': 0, 'projects': 0, 'enabled': 0, 'list': 0,
                  'with_participants': 1, 'with_sites': 1, 'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        params = {'id_site': 1, 'projects': 1, 'enabled': 1, 'list': 0,
                  'with_participants': 0, 'with_sites': 1, 'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self._checkJson(json_data=response.json, params=params)

        params = {'id_site': 100, 'projects': 0, 'enabled': 0, 'list': 1,
                  'with_participants': 1, 'with_sites': 0, 'with_status': 0}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        params = {'id_project': 0, 'projects': 1, 'enabled': 0, 'list': 1,
                  'with_participants': 1, 'with_sites': 1, 'with_status': 0}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        params = {'id_project': 1, 'projects': 1, 'enabled': 1, 'list': 1,
                  'with_participants': 1, 'with_sites': 0, 'with_status': 0}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self._checkJson(json_data=response.json, params=params)

        params = {'id_project': 100, 'projects': 1, 'enabled': 0, 'list': 0,
                  'with_participants': 1, 'with_sites': 1, 'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        params = {'id_device_type': 0, 'projects': 1, 'enabled': 0, 'list': 0,
                  'with_participants': 1, 'with_sites': 1, 'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        params = {'id_device_type': 1, 'projects': 1, 'enabled': 0, 'list': 0,
                  'with_participants': 1, 'with_sites': 0, 'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self._checkJson(json_data=response.json, params=params)

        params = {'id_device_type': 100, 'projects': 0, 'enabled': 0, 'list': 1,
                  'with_participants': 1, 'with_sites': 1, 'with_status': 0}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        params = {'id_device_subtype': 0, 'projects': 1, 'enabled': 0, 'list': 0,
                  'with_participants': 1, 'with_sites': 1, 'with_status': 0}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        # Can't test because no id_device_subtypes available in DB
        # params = {'id_device_subtype': 'Null', 'projects': flags[0], 'enabled': flags[1], 'list': flags[2],
        #           'with_participants': flags[3], 'with_sites': flags[4], 'with_status': flags[5]}
        # response = self._request_with_http_auth(username='admin', password='admin', payload=params)
        # self.assertEqual(response.status_code, 200)
        # self._checkJson(json_data=response.json(), params=params)

        params = {'id_device_subtype': 100, 'projects': 0, 'enabled': 1, 'list': 0,
                  'with_participants': 0, 'with_sites': 0, 'with_status': 0}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        params = {'name': " ", 'projects': 1, 'enabled': None, 'list': None,
                  'with_participants': None, 'with_sites': 1, 'with_status': 0}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

        params = {'name': "Apple Watch #W05P1", 'projects': None, 'enabled': 0, 'list': 1,
                  'with_participants': 0, 'with_sites': None, 'with_status': None}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self._checkJson(json_data=response.json, params=params)

        params = {'name': "Apple Watch", 'projects': 0, 'enabled': 0, 'list': 0,
                  'with_participants': 1, 'with_sites': 0, 'with_status': 1}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 0)

    def test_query_post_as_admin(self):
        new_id = []
        # No param
        params = {}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 400)

        # Creating a device without the needed info (minimal info is id_device =0, device_name and id_device_type)
        params = {"device": {"device_name": "Test", "id_device": 0}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 500)

        # Creating a device without the needed info (minimal info is id_device =0, device_name and id_device_type)
        params = {"device": {"id_device_type": 2, "id_device": 0}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 500)

        # Creating a device without a good device type
        params = {"device": {"device_name": "Test", "id_device": 0, 'id_device_type': 100}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 500)

        # Creating a good device with minimal info
        params = {"device": {"device_name": "Test", "id_device": 0, 'id_device_type': 3}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 200)
        new_id.append(response.json[0]['id_device'])
        self._checkJsonPost(json_data=response.json)

        # Creating a bad device with a bad subtype id
        params = {"device": {"device_name": "Test", "id_device": 0, 'id_device_type': 3, "id_device_subtype": 100}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 500)

        # Creating a good device with good subtype id info
        params = {"device": {"device_name": "Test", "id_device": 0, 'id_device_type': 3, "id_device_subtype": 2}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 200)
        new_id.append(response.json[0]['id_device'])
        self._checkJsonPost(json_data=response.json)

        # Creating a device with all the infos (device uuid, token, last_online makes a 500 error)
        params = {"device": {"device_certificate": "Un certificat", "device_config": "Une configuration",
                             "device_enabled": False, "device_infos": "Une info",
                             # "device_lastonline": "2020-10-19T17:51:25.251Z",
                             "device_name": "Un nom", "device_notes": "Une note", "device_onlineable": False,
                             "device_token": "Un Token", "device_uuid": "Un uuid",
                             "id_device": 0, "id_device_subtype": 1, "id_device_type": 1}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 200)
        new_id.append(response.json[0]['id_device'])
        self._checkJsonPost(json_data=response.json)

        # Update a device with a wrongful id_device_type
        params = {"device": {"device_certificate": "Un certificat 2", "device_config": "Une configuration 2",
                             "device_enabled": True, "device_infos": "Une info 2",
                             # "device_lastonline": "En ligne la derniere fois 2",
                             "device_name": "Un nom 2", "device_notes": "Une note 2", "device_onlineable": True,
                             "device_token": "Un Token @", "device_uuid": "Un uuid @",
                             "id_device": new_id[2], "id_device_subtype": 100, "id_device_type": 1}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 500)

        # Update a device with a correct id_device_type but with a change in device_lastonlice
        params = {"device": {"device_certificate": "Un certificat 2", "device_config": "Une configuration 2",
                             "device_enabled": True, "device_infos": "Une info 2",
                             # "device_lastonline": "En ligne la derniere fois 2",
                             "device_name": "Un nom 2", "device_notes": "Une note 2", "device_onlineable": True,
                             "device_token": "Un Token @", "device_uuid": "Un uuid @",
                             "id_device": new_id[2], "id_device_subtype": 2, "id_device_type": 2}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 200)
        self._checkJsonPost(json_data=response.json)

        # Update a device with a correct id_device
        params = {"device": {"id_device": new_id[2], "id_device_subtype": 1, "id_device_type": 1}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 200)
        self._checkJsonPost(json_data=response.json)

        # deleting created and updated devices
        for id_to_del in new_id:
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': id_to_del})
            self.assertEqual(response.status_code, 200)

    def test_query_post_as_user(self):
        # Access Test
        params = {"device": {"device_name": "Test", "id_device": 0, 'id_device_type': 3}}
        response = self._post_with_user_http_auth(self.test_client, username='user4', password='user4', json=params)
        self.assertEqual(response.status_code, 403)

    def test_query_delete_as_admin(self):
        new_id = []
        # Creating a good device with minimal info
        params = {"device": {"device_name": "Test", "id_device": 0, 'id_device_type': 3}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 200)
        self._checkJsonPost(json_data=response.json)
        new_id.append(response.json[0]['id_device'])

        # Delete without id
        params = {}
        response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                    params={'id': params})
        self.assertEqual(response.status_code, 400)

        # Delete an unexisting ID
        response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                    params={'id': new_id[0]+1})
        self.assertEqual(response.status_code, 400)

        # Delete the device
        response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                    params={'id': new_id[0]})
        self.assertEqual(response.status_code, 200)

    def test_query_delete_exceptions_as_admin(self):
        with self._flask_app.app_context():
            # Create a new device
            params = {"device": {"device_name": "Test", "id_device": 0, 'id_device_type': 3}}
            response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
            self.assertEqual(response.status_code, 200)
            self._checkJsonPost(json_data=response.json)
            device_id = response.json[0]['id_device']

            # Create associated items
            dev_part = TeraDeviceParticipant()
            dev_part.from_json({'id_device': device_id, 'id_participant': 1})
            TeraDeviceParticipant.insert(dev_part)

            json_session = {'id_session_type': 1,
                            'session_name': 'Session #1',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0
                            }
            session1 = TeraSession()
            session1.from_json(json_session)
            TeraSession.insert(session1)

            dev_session = TeraSessionDevices()
            dev_session.from_json({'id_device': device_id, 'id_session': session1.id_session})
            TeraSessionDevices.insert(dev_session)

            json_session = {'id_session_type': 1,
                            'session_name': 'Session #2',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            'id_creator_device': device_id
                            }
            session2 = TeraSession()
            session2.from_json(json_session)
            TeraSession.insert(session2)

            json_session = {'id_session_type': 1,
                            'session_name': 'Session #3',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            }
            session3 = TeraSession()
            session3.from_json(json_session)
            TeraSession.insert(session3)
            json_session = {'id_session_type': 1,
                            'session_name': 'Session #4',
                            'session_start_datetime': datetime.datetime.now(),
                            'session_status': 0,
                            }
            session4 = TeraSession()
            session4.from_json(json_session)
            TeraSession.insert(session4)
            json_test = {'id_test_type': 1,
                         'id_session': session3.id_session,
                         'test_name': 'Test Test',
                         'id_device': device_id,
                         'test_datetime': datetime.datetime.now()
                         }
            new_test = TeraTest()
            new_test.from_json(json_test)
            TeraTest.insert(new_test)
            service_uuid = TeraService.get_openteraserver_service().service_uuid
            json_asset = {'id_session': session4.id_session,
                          'id_device': device_id,
                          'asset_name': 'Test Asset',
                          'asset_type': 'Test asset',
                          'asset_service_uuid': service_uuid}
            new_asset = TeraAsset()
            new_asset.from_json(json_asset)
            TeraAsset.insert(new_asset)

            # Delete operations
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': device_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, associated to participants")

            TeraDeviceParticipant.delete(dev_part.id_device_participant)
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': device_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, associated to sessions")

            TeraSession.delete(session1.id_session)
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': device_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has created sessions")

            TeraSession.delete(session2.id_session)
            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': device_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has assets")
            TeraAsset.delete(new_asset.id_asset)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': device_id})
            self.assertEqual(response.status_code, 500, msg="Can't delete, has tests")
            TeraTest.delete(new_test.id_test)

            response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                        params={'id': device_id})
            self.assertEqual(response.status_code, 200, msg="Delete OK")

    def test_query_delete_as_user(self):
        new_id = []
        # Creating a good device with minimal info
        params = {"device": {"device_name": "Test", "id_device": 0, 'id_device_type': 3}}
        response = self._post_with_user_http_auth(self.test_client, username='admin', password='admin', json=params)
        self.assertEqual(response.status_code, 200)
        new_id.append(response.json[0]['id_device'])
        self._checkJsonPost(json_data=response.json)

        # Delete as user
        response = self._delete_with_user_http_auth(self.test_client, username='user4', password='user4',
                                                    params={'id': new_id[0]})
        self.assertEqual(response.status_code, 403)

        # Delete the device
        response = self._delete_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                    params={'id': new_id[0]})
        self.assertEqual(response.status_code, 200)

    def test_query_device_with_status_as_admin(self):
        params = {'with_status': True}
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin', params=params)
        self.assertEqual(response.status_code, 200)

        # Check for important status fields
        for device_info in response.json:
            self.assertTrue('device_online' in device_info)
            self.assertTrue('device_busy' in device_info)
            self.assertTrue('device_status' in device_info)
