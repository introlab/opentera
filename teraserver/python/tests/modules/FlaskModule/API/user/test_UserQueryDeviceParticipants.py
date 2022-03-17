from typing import List

from BaseUserAPITest import BaseUserAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraDeviceSite import TeraDeviceSite
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraUser import TeraUser


class UserQueryDeviceParticipantsTest(BaseUserAPITest):
    test_endpoint = '/api/user/deviceparticipants'

    def setUp(self):
        super().setUp()
        from modules.FlaskModule.FlaskModule import user_api_ns
        from BaseUserAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.user.UserQueryDeviceParticipants import UserQueryDeviceParticipants
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseUserAPITest.getConfig())}
        user_api_ns.add_resource(UserQueryDeviceParticipants, '/deviceparticipants', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        response = self.test_client.get(self.test_endpoint)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_http_auth(self):
        response = self._get_with_user_http_auth(self.test_client)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_invalid_token_auth(self):
        response = self._get_with_user_token_auth(self.test_client)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_http_auth_admin_and_no_params(self):
        response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin')
        self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_http_auth_admin_and_id_device(self):
        devices: List[TeraDevice] = TeraDevice.query.all()

        for device in devices:
            params = {
                'id_device': device.id_device,
                'list': True
            }
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            self.session.add(device)  # Required for lazy loading
            self.assertEqual(len(device.device_participants), len(response.json))

            # May not be in same order
            participant_ids = [participant.id_participant for participant in device.device_participants]
            for index in range(len(response.json)):
                self.assertTrue(response.json[index]['id_participant'] in participant_ids)

    def test_get_endpoint_with_http_auth_admin_and_id_participant(self):
        participants: List[TeraParticipant] = TeraParticipant.query.all()

        for participant in participants:
            params = {
                'id_participant': participant.id_participant,
                'list': True
            }
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)
            # self.session.add(participant)  # Required for lazy loading
            self.assertEqual(len(participant.participant_devices), len(response.json))

            # Assuming same order here
            for index in range(len(response.json)):
                self.assertEqual(participant.participant_devices[index].id_device,
                                 response.json[index]['id_device'])

    def test_get_endpoint_with_http_auth_admin_and_id_site(self):
        sites: List[TeraSite] = TeraSite.query.all()

        for site in sites:
            params = {
                'id_site': site.id_site,
                'list': True
            }
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            self.assertEqual(200, response.status_code)

            from modules.DatabaseModule.DBManager import DBManager
            user: TeraUser = TeraUser.get_user_by_username('admin')
            self.assertIsNotNone(user)
            user_access = DBManager.userAccess(user)
            self.assertIsNotNone(user_access)
            self.assertEqual(len(user_access.query_device_participants_for_site(site.id_site)), len(response.json))

    def test_get_endpoint_with_http_auth_admin_and_id_device_type_no_participant(self):
        device_types: List[TeraDeviceType] = TeraDeviceType.query.all()

        for device_type in device_types:
            params = {
                'id_device_type': device_type.id_device_type,
                'list': True
            }
            response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                     params=params)
            # Maybe should be 400 because of missing id_participant ?
            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.json))

    def test_get_endpoint_with_http_auth_admin_and_id_device_type_valid_participant(self):
        participants: List[TeraParticipant] = TeraParticipant.query.all()

        for participant in participants:
            device_types: List[TeraDeviceType] = TeraDeviceType.query.all()

            for device_type in device_types:
                params = {
                    'id_device_type': device_type.id_device_type,
                    'id_participant': participant.id_participant,
                    'list': True
                }
                response = self._get_with_user_http_auth(self.test_client, username='admin', password='admin',
                                                         params=params)

                self.assertEqual(200, response.status_code)
                from modules.DatabaseModule.DBManager import DBManager
                user: TeraUser = TeraUser.get_user_by_username('admin')
                self.assertIsNotNone(user)
                user_access = DBManager.userAccess(user)
                self.assertIsNotNone(user_access)
                self.assertEqual(len(user_access.query_device_participants_by_type
                                     (device_type.id_device_type, participant.id_participant)), len(response.json))
