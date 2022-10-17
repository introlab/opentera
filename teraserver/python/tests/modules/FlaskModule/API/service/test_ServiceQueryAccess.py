from typing import List

from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraUser import TeraUser
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from modules.DatabaseModule.DBManagerTeraParticipantAccess import DBManagerTeraParticipantAccess
from modules.DatabaseModule.DBManagerTeraDeviceAccess import DBManagerTeraDeviceAccess
import uuid


class ServiceQueryAccessTest(BaseServiceAPITest):
    test_endpoint = '/api/service/access'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import service_api_ns
        from BaseServiceAPITest import FakeFlaskModule

        # Setup minimal API
        from modules.FlaskModule.API.service.ServiceQueryAccess import ServiceQueryAccess
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseServiceAPITest.getConfig())}
        service_api_ns.add_resource(ServiceQueryAccess, '/access', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        with flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_invalid_user_uuid(self):
        with flask_app.app_context():
            for admin in [True, False]:
                params = {
                    'from_user_uuid': str(uuid.uuid4()),
                    'admin': admin,
                    'with_users_uuids': True,
                    'with_projects_ids': True,
                    'with_participants_uuids': True,
                    'with_devices_uuids': True,
                    'with_sites_ids': True
                }

                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_invalid_participant_uuid_or_invalid_admin(self):
        with flask_app.app_context():
            for admin in [True, False]:
                params = {
                    'from_participant_uuid': str(uuid.uuid4()),
                    'admin': admin,
                    'with_users_uuids': True,
                    'with_projects_ids': True,
                    'with_participants_uuids': True,
                    'with_devices_uuids': True,
                    'with_sites_ids': True
                }

                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_invalid_device_uuid_or_invalid_admin(self):
        with flask_app.app_context():
            for admin in [True, False]:
                params = {
                    'from_device_uuid': str(uuid.uuid4()),
                    'admin': admin,
                    'with_users_uuids': True,
                    'with_projects_ids': True,
                    'with_participants_uuids': True,
                    'with_devices_uuids': True,
                    'with_sites_ids': True
                }

                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_all_params_admin_and_not_admin_for_user_uuids(self):
        with flask_app.app_context():
            for admin in [True, False]:
                # Test for all users
                for user in TeraUser.query.all():
                    params = {
                        'from_user_uuid':  user.user_uuid,
                        'admin': admin,
                        'with_users_uuids': True,
                        'with_projects_ids': True,
                        'with_participants_uuids': True,
                        'with_devices_uuids': True,
                        'with_sites_ids': True
                    }

                    response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                                 params=params, endpoint=self.test_endpoint)
                    self.assertEqual(200, response.status_code)
                    self.assertTrue(response.is_json)

                    self.assertTrue('from_user_uuid' in response.json)
                    self.assertTrue('admin' in response.json)
                    self.assertTrue('users_uuids' in response.json)
                    self.assertTrue('projects_ids' in response.json)
                    self.assertTrue('participants_uuids' in response.json)
                    self.assertTrue('devices_uuids' in response.json)
                    self.assertTrue('sites_ids' in response.json)

                    access = DBManagerTeraUserAccess(user)
                    self.assertEqual(response.json['users_uuids'], access.get_accessible_users_uuids(admin))
                    self.assertEqual(response.json['projects_ids'], access.get_accessible_projects_ids(admin))
                    self.assertEqual(response.json['participants_uuids'], access.get_accessible_participants_uuids(admin))
                    self.assertEqual(response.json['devices_uuids'], access.get_accessible_devices_uuids(admin))
                    self.assertEqual(response.json['sites_ids'], access.get_accessible_sites_ids(admin))

    def test_get_endpoint_with_token_auth_all_params_admin_and_not_admin_for_participant_uuids(self):
        with flask_app.app_context():
            for admin in [True, False]:
                # Test for all users
                for participant in TeraParticipant.query.all():
                    params = {
                        'from_participant_uuid':  participant.participant_uuid,
                        'admin': admin,
                        'with_users_uuids': True,
                        'with_projects_ids': True,
                        'with_participants_uuids': True,
                        'with_devices_uuids': True,
                        'with_sites_ids': True
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
                    self.assertTrue('users_uuids' in response.json)
                    self.assertTrue('projects_ids' in response.json)
                    self.assertTrue('participants_uuids' in response.json)
                    self.assertTrue('devices_uuids' in response.json)
                    self.assertTrue('sites_ids' in response.json)

                    # TODO complete tests with participants
                    # access = DBManagerTeraParticipantAccess(participant)

    def test_get_endpoint_with_token_auth_all_params_admin_and_not_admin_for_participant_uuids(self):
        with flask_app.app_context():
            for admin in [True, False]:
                # Test for all users
                for device in TeraDevice.query.all():
                    params = {
                        'from_device_uuid':  device.device_uuid,
                        'admin': admin,
                        'with_users_uuids': True,
                        'with_projects_ids': True,
                        'with_participants_uuids': True,
                        'with_devices_uuids': True,
                        'with_sites_ids': True
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
                    self.assertTrue('users_uuids' in response.json)
                    self.assertTrue('projects_ids' in response.json)
                    self.assertTrue('participants_uuids' in response.json)
                    self.assertTrue('devices_uuids' in response.json)
                    self.assertTrue('sites_ids' in response.json)

                    # TODO complete tests with devices
                    access = DBManagerTeraDeviceAccess(device)

