from BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraUser import TeraUser
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from modules.DatabaseModule.DBManagerTeraDeviceAccess import DBManagerTeraDeviceAccess
import uuid


class ServiceQueryAccessTest(BaseServiceAPITest):
    test_endpoint = '/api/service/access'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_invalid_user_uuid(self):
        with self._flask_app.app_context():
            for admin in [True, False]:
                params = {
                    'from_user_uuid': str(uuid.uuid4()),
                    'admin': admin,
                    'with_users': True,
                    'with_projects': True,
                    'with_participants': True,
                    'with_devices': True,
                    'with_sites': True
                }

                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_invalid_participant_uuid_or_invalid_admin(self):
        with self._flask_app.app_context():
            for admin in [True, False]:
                params = {
                    'from_participant_uuid': str(uuid.uuid4()),
                    'admin': admin,
                    'with_users': True,
                    'with_projects': True,
                    'with_participants': True,
                    'with_devices': True,
                    'with_sites': True
                }

                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_invalid_device_uuid_or_invalid_admin(self):
        with self._flask_app.app_context():
            for admin in [True, False]:
                params = {
                    'from_device_uuid': str(uuid.uuid4()),
                    'admin': admin,
                    'with_users': True,
                    'with_projects': True,
                    'with_participants': True,
                    'with_devices': True,
                    'with_sites': True
                }

                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_all_params_admin_and_not_admin_for_user_uuids(self):
        with self._flask_app.app_context():
            for admin in [True, False]:
                # Test for all users
                for user in TeraUser.query.all():
                    params = {
                        'from_user_uuid':  user.user_uuid,
                        'admin': admin,
                        'with_users': True,
                        'with_projects': True,
                        'with_participants': True,
                        'with_devices': True,
                        'with_sites': True,
                        'with_names': True
                    }

                    response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                                 params=params, endpoint=self.test_endpoint)
                    self.assertEqual(200, response.status_code)
                    self.assertTrue(response.is_json)

                    self.assertTrue('from_user_uuid' in response.json)
                    self.assertTrue('admin' in response.json)
                    self.assertTrue('users' in response.json)
                    if response.json['users']:
                        self.assertTrue('uuid' in response.json['users'][0])
                        self.assertTrue('name' in response.json['users'][0])
                    self.assertTrue('projects' in response.json)
                    self.assertTrue('participants' in response.json)
                    self.assertTrue('devices' in response.json)
                    self.assertTrue('sites' in response.json)

                    access = DBManagerTeraUserAccess(user)
                    users = access.get_accessible_users(admin)
                    self.assertEqual([user.user_uuid for user in users],
                                     [user['uuid'] for user in response.json['users']])
                    self.assertEqual([user.get_fullname() for user in users],
                                     [user['name'] for user in response.json['users']])
                    projects = access.get_accessible_projects(admin)
                    self.assertEqual([proj.id_project for proj in projects],
                                     [proj['id'] for proj in response.json['projects']])
                    self.assertEqual([proj.project_name for proj in projects],
                                     [proj['name'] for proj in response.json['projects']])
                    participants = access.get_accessible_participants(admin)
                    self.assertEqual([part.participant_uuid for part in participants],
                                     [part['uuid'] for part in response.json['participants']])
                    self.assertEqual([part.participant_name for part in participants],
                                     [part['name'] for part in response.json['participants']])
                    devices = access.get_accessible_devices(admin)
                    self.assertEqual([dev.device_uuid for dev in devices],
                                     [dev['uuid'] for dev in response.json['devices']])
                    self.assertEqual([dev.device_name for dev in devices],
                                     [dev['name'] for dev in response.json['devices']])
                    sites = access.get_accessible_sites(admin)
                    self.assertEqual([site.id_site for site in sites],
                                     [site['id'] for site in response.json['sites']])
                    self.assertEqual([site.site_name for site in sites],
                                     [site['name'] for site in response.json['sites']])

    def test_get_endpoint_with_token_auth_all_params_admin_and_not_admin_for_participant_uuids(self):
        with self._flask_app.app_context():
            for admin in [True, False]:
                # Test for all users
                for participant in TeraParticipant.query.all():
                    params = {
                        'from_participant_uuid':  participant.participant_uuid,
                        'admin': admin,
                        'with_users': True,
                        'with_projects': True,
                        'with_participants': True,
                        'with_devices': True,
                        'with_sites': True,
                        'with_names': True
                    }

                    response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                                 params=params, endpoint=self.test_endpoint)
                    if admin:
                        self.assertEqual(400, response.status_code)
                        continue

                    self.assertEqual(200, response.status_code)
                    self.assertTrue(response.is_json)

                    self.assertTrue('from_participant_uuid' in response.json)
                    self.assertFalse('admin' in response.json)
                    self.assertTrue('users' in response.json)
                    if response.json['users']:
                        self.assertTrue('uuid' in response.json['users'][0])
                        self.assertTrue('name' in response.json['users'][0])
                    self.assertTrue('projects' in response.json)
                    self.assertTrue('participants' in response.json)
                    self.assertTrue('devices' in response.json)
                    self.assertTrue('sites' in response.json)

                    # TODO complete tests with participants
                    # access = DBManagerTeraParticipantAccess(participant)

    def test_get_endpoint_with_token_auth_all_params_admin_and_not_admin_for_device_uuids(self):
        with self._flask_app.app_context():
            for admin in [True, False]:
                # Test for all users
                for device in TeraDevice.query.all():
                    params = {
                        'from_device_uuid':  device.device_uuid,
                        'admin': admin,
                        'with_users': True,
                        'with_projects': True,
                        'with_participants': True,
                        'with_devices': True,
                        'with_sites': True,
                        'with_names': True
                    }

                    response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                                 params=params, endpoint=self.test_endpoint)
                    if admin:
                        self.assertEqual(400, response.status_code)
                        continue

                    self.assertEqual(200, response.status_code)
                    self.assertTrue(response.is_json)

                    self.assertTrue('from_device_uuid' in response.json)
                    self.assertFalse('admin' in response.json)
                    self.assertTrue('users' in response.json)
                    if response.json['users']:
                        self.assertTrue('uuid' in response.json['users'][0])
                        self.assertTrue('name' in response.json['users'][0])
                    self.assertTrue('projects' in response.json)
                    self.assertTrue('participants' in response.json)
                    self.assertTrue('devices' in response.json)
                    self.assertTrue('sites' in response.json)

                    # TODO complete tests with devices
                    access = DBManagerTeraDeviceAccess(device)

