from typing import List

from tests.modules.FlaskModule.API.service.BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraService import TeraService
from modules.DatabaseModule.DBManagerTeraServiceAccess import DBManagerTeraServiceAccess
import uuid


class ServiceQueryDisconnectTest(BaseServiceAPITest):
    test_endpoint = '/api/service/disconnect'

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

    def test_get_endpoint_with_invalid_id_user(self):
        with self._flask_app.app_context():
            params = {'id_user': 12345}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_id_user(self):
        with self._flask_app.app_context():
            for user in TeraUser.query.all():
                params = {'id_user': user.id_user}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)

                service = TeraService.get_service_by_key('VideoRehabService')
                service_access = DBManagerTeraServiceAccess(service)

                if user.id_user in service_access.get_accessible_users_ids():
                    self.assertEqual(200, response.status_code)
                else:
                    self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_invalid_user_uuid(self):
        with self._flask_app.app_context():
            params = {'user_uuid': str(uuid.uuid4())}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_user_uuid(self):
        with self._flask_app.app_context():
            for user in TeraUser.query.all():
                params = {'user_uuid': user.user_uuid}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)

                service = TeraService.get_service_by_key('VideoRehabService')
                service_access = DBManagerTeraServiceAccess(service)

                if user.user_uuid in service_access.get_accessible_users_uuids():
                    self.assertEqual(200, response.status_code)
                else:
                    self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_invalid_id_participant(self):
        with self._flask_app.app_context():
            params = {'id_participant': 12345}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_id_participant(self):
        with self._flask_app.app_context():
            for participant in TeraParticipant.query.all():
                params = {'id_participant': participant.id_participant}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)

                service = TeraService.get_service_by_key('VideoRehabService')
                service_access = DBManagerTeraServiceAccess(service)

                if participant.id_participant in service_access.get_accessible_participants_ids():
                    self.assertEqual(200, response.status_code)
                else:
                    self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_invalid_participant_uuid(self):
        with self._flask_app.app_context():
            params = {'participant_uuid': str(uuid.uuid4())}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_participant_uuid(self):
        with self._flask_app.app_context():
            for participant in TeraParticipant.query.all():
                params = {'participant_uuid': participant.participant_uuid}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)

                service = TeraService.get_service_by_key('VideoRehabService')
                service_access = DBManagerTeraServiceAccess(service)

                if participant.participant_uuid in service_access.get_accessible_participants_uuids():
                    self.assertEqual(200, response.status_code)
                else:
                    self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_invalid_id_device(self):
        with self._flask_app.app_context():
            params = {'id_device': 12345}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_id_device(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                params = {'id_device': device.id_device}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)

                service = TeraService.get_service_by_key('VideoRehabService')
                service_access = DBManagerTeraServiceAccess(service)

                if device.id_device in service_access.get_accessible_devices_ids():
                    self.assertEqual(200, response.status_code)
                else:
                    self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_invalid_device_uuid(self):
        with self._flask_app.app_context():
            params = {'device_uuid': str(uuid.uuid4())}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_valid_device_uuid(self):
        with self._flask_app.app_context():
            for device in TeraDevice.query.all():
                params = {'device_uuid': device.device_uuid}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)

                service = TeraService.get_service_by_key('VideoRehabService')
                service_access = DBManagerTeraServiceAccess(service)

                if device.device_uuid in service_access.get_accessible_devices_uuids():
                    self.assertEqual(200, response.status_code)
                else:
                    self.assertEqual(403, response.status_code)
