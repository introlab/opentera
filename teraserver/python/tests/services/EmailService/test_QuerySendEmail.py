from tests.services.EmailService.BaseEmailServiceAPITest import BaseEmailServiceAPITest
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraUser import TeraUser
from opentera.services.ServiceAccessManager import ServiceAccessManager


class EmailSendEmailTest(BaseEmailServiceAPITest):
    test_endpoint = '/api/send'

    def setUp(self):
        super().setUp()
        with self.app_context():
            user: TeraUser = TeraUser.get_user_by_username('admin')
            service = TeraService.get_service_by_key('FileTransferService')
            self.assertIsNotNone(user)
            self.assertIsNotNone(service)
            self.user_admin_token = user.get_token(ServiceAccessManager.api_user_token_key)
            self.assertIsNotNone(self.user_admin_token)
            self.assertGreater(len(self.user_admin_token), 0)

            user: TeraUser = TeraUser.get_user_by_username('user3')
            self.assertIsNotNone(user)
            self.user_user3_token = user.get_token(ServiceAccessManager.api_user_token_key)
            self.assertIsNotNone(self.user_user3_token)
            self.assertGreater(len(self.user_user3_token), 0)

    def tearDown(self):
        super().tearDown()

    def test_post_endpoint_with_invalid_token(self):
        with self.app_context():
            response = self._post_with_token_auth(self.test_client, token="invalid")
            self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_static_participant_token(self):
        with self.app_context():
            for participant in TeraParticipant.query.all():
                self.assertIsNotNone(participant)
                if participant.participant_enabled and participant.participant_token:
                    self.assertIsNotNone(participant.participant_token)
                    self.assertGreater(len(participant.participant_token), 0)
                    response = self._post_with_token_auth(self.test_client, token=participant.participant_token)
                    self.assertEqual(response.status_code, 403)

    def test_post_endpoint_with_static_device_token(self):
        with self.app_context():
            for device in TeraDevice.query.all():
                self.assertIsNotNone(device)
                if device.device_enabled:
                    device_token = device.device_token
                    self.assertIsNotNone(device_token)
                    self.assertGreater(len(device_token), 0)
                    response = self._post_with_token_auth(self.test_client, token=device_token)
                    self.assertEqual(response.status_code, 401)

    def test_get_endpoint_with_service_token_no_params(self):
        with self.app_context():
            service: TeraService = TeraService.get_service_by_key('EmailService')
            self.assertIsNotNone(service)
            service_token = service.get_token(ServiceAccessManager.api_service_token_key)
            self.assertGreater(len(service_token), 0)
            response = self._post_with_token_auth(self.test_client, token=service_token)
            self.assertEqual(response.status_code, 403)

    def test_missing_uuids(self):
        with self.app_context():
            json_data = {}
            response = self._post_with_token_auth(self.test_client, token=self.user_admin_token, json=json_data)
            self.assertEqual(response.status_code, 400)

    def test_forbidden_user_uuids(self):
        with self.app_context():
            admin_uuid = TeraUser.get_user_by_username('admin').user_uuid
            self.assertIsNotNone(admin_uuid)
            json_data={'user_uuid': admin_uuid}
            response = self._post_with_token_auth(self.test_client, token=self.user_user3_token, json=json_data)
            self.assertEqual(response.status_code, 403)
