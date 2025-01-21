from services.EmailService.libemailservice.db.models import EmailTemplate
from tests.services.EmailService.BaseEmailServiceAPITest import BaseEmailServiceAPITest
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraUser import TeraUser
from opentera.services.ServiceAccessManager import ServiceAccessManager
import services.EmailService.Globals as Globals


class EmailSendEmailTest(BaseEmailServiceAPITest):
    test_endpoint = '/api/send'

    def setUp(self):
        super().setUp()

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
            json_data = {'user_uuid': admin_uuid}
            response = self._post_with_token_auth(self.test_client, token=self.user_user3_token, json=json_data)
            self.assertEqual(response.status_code, 403)

            json_data = {'user_uuid': [admin_uuid, '11111111']}
            response = self._post_with_token_auth(self.test_client, token=self.user_admin_token, json=json_data)
            self.assertEqual(response.status_code, 403)

    def test_forbidden_participant_uuids(self):
        with self.app_context():
            part_uuid = TeraParticipant.get_participant_by_username('participant1').participant_uuid
            self.assertIsNotNone(part_uuid)
            json_data = {'participant_uuid': part_uuid}
            response = self._post_with_token_auth(self.test_client, token=self.user_user4_token, json=json_data)
            self.assertEqual(response.status_code, 403)

            json_data = {'participant_uuid': [part_uuid, '11111111']}
            response = self._post_with_token_auth(self.test_client, token=self.user_admin_token, json=json_data)
            self.assertEqual(response.status_code, 403)

    def test_template_and_body_content(self):
        with self.app_context():
            json_data = {'id_template': 1, 'body': "This is a test email"}
            response = self._post_with_token_auth(self.test_client, token=self.user_admin_token, json=json_data)
            self.assertEqual(response.status_code, 400)

    def test_missing_body_and_template(self):
        with self.app_context():
            part_uuid = TeraParticipant.get_participant_by_username('participant1').participant_uuid
            self.assertIsNotNone(part_uuid)
            json_data = {'participant_uuid': part_uuid}
            response = self._post_with_token_auth(self.test_client, token=self.user_admin_token, json=json_data)
            self.assertEqual(response.status_code, 400)

    def test_sender_no_email(self):
        with self.app_context():
            part_uuid = TeraParticipant.get_participant_by_name('Participant #2').participant_uuid
            self.assertIsNotNone(part_uuid)
            json_data = {'participant_uuid': part_uuid, 'body': 'This is a test email'}
            response = self._post_with_token_auth(self.test_client, token=self.user_user3_token, json=json_data)
            self.assertEqual(response.status_code, 400)

    def test_invalid_template(self):
        with self.app_context():
            part_uuid = TeraParticipant.get_participant_by_username('participant1').participant_uuid
            self.assertIsNotNone(part_uuid)
            json_data = {'participant_uuid': part_uuid, 'id_template': 0}
            response = self._post_with_token_auth(self.test_client, token=self.user_admin_token, json=json_data)
            self.assertEqual(response.status_code, 403)

    def test_no_access_to_template_site(self):
        with self.app_context():
            user_uuid = TeraUser.get_user_by_username('user4').user_uuid
            self.assertIsNotNone(user_uuid)
            template = EmailTemplate.get_template_by_key('SITE_EMAIL')
            self.assertIsNotNone(template)
            json_data = {'user_uuid': user_uuid, 'id_template': template.id_email_template}
            response = self._post_with_token_auth(self.test_client, token=self.user_user4_token, json=json_data)
            self.assertEqual(response.status_code, 403)

    def test_no_access_to_template_project(self):
        with self.app_context():
            user_uuid = TeraUser.get_user_by_username('user4').user_uuid
            self.assertIsNotNone(user_uuid)
            template = EmailTemplate.get_template_by_key('PROJECT_EMAIL')
            self.assertIsNotNone(template)
            json_data = {'user_uuid': user_uuid, 'id_template': template.id_email_template}
            response = self._post_with_token_auth(self.test_client, token=self.user_user4_token, json=json_data)
            self.assertEqual(response.status_code, 403)

    def test_no_access_to_global_template(self):
        with self.app_context():
            part_uuid = TeraParticipant.get_participant_by_username('participant1').participant_uuid
            self.assertIsNotNone(part_uuid)
            template = EmailTemplate.get_template_by_key('GENERAL_TEST_EMAIL')
            self.assertIsNotNone(template)
            json_data = {'participant_uuid': part_uuid, 'id_template': template.id_email_template}
            response = self._post_with_token_auth(self.test_client, token=self.user_user3_token, json=json_data)
            self.assertEqual(response.status_code, 403)

    def test_send_success_with_template(self):
        with self.app_context():
            part_uuid = TeraParticipant.get_participant_by_username('participant1').participant_uuid
            self.assertIsNotNone(part_uuid)
            template = EmailTemplate.get_template_by_key('GENERAL_TEST_EMAIL')
            self.assertIsNotNone(template)
            json_data = {'participant_uuid': part_uuid, 'id_template': template.id_email_template,
                         'body_variables': {'variable': 'V1Test'}}
            with Globals.service.flask_module.mail_man.record_messages() as outbox:
                response = self._post_with_token_auth(self.test_client, token=self.user_admin_token, json=json_data)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(outbox), 1)
                self.assertTrue('GLOBAL' in outbox[0].html)
                self.assertTrue('V1Test' in outbox[0].html)

    def test_send_success(self):
        with self.app_context():
            part_uuid = TeraParticipant.get_participant_by_username('participant1').participant_uuid
            self.assertIsNotNone(part_uuid)
            json_data = {'participant_uuid': part_uuid, 'body': 'This is a test email', 'subject': 'Test Email'}
            with Globals.service.flask_module.mail_man.record_messages() as outbox:
                response = self._post_with_token_auth(self.test_client, token=self.user_admin_token, json=json_data)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(outbox), 1)
                self.assertEqual(outbox[0].subject, "Test Email")


    def test_send_with_variables(self):
        with self.app_context():
            part_uuid = TeraParticipant.get_participant_by_username('participant1').participant_uuid
            self.assertIsNotNone(part_uuid)
            json_data = {'participant_uuid': part_uuid, 'body': 'Variable #1 = $variable1, Variable #2 = $variable2',
                         'subject': 'Test Email', 'body_variables': {'variable1': 'Unit', 'variable2': 'Test'}}
            with Globals.service.flask_module.mail_man.record_messages() as outbox:
                response = self._post_with_token_auth(self.test_client, token=self.user_admin_token, json=json_data)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(outbox), 1)
                self.assertEqual(outbox[0].html, "Variable #1 = Unit, Variable #2 = Test")
