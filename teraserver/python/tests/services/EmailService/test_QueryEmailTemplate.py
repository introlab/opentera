from services.EmailService.libemailservice.db.models import EmailTemplate
from tests.services.EmailService.BaseEmailServiceAPITest import BaseEmailServiceAPITest
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraUser import TeraUser
from opentera.services.ServiceAccessManager import ServiceAccessManager
import services.EmailService.Globals as Globals


class EmailEmailTemplateTest(BaseEmailServiceAPITest):
    test_endpoint = '/api/templates'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_with_invalid_token(self):
        with self.app_context():
            response = self._get_with_token_auth(self.test_client, token="invalid")
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_with_static_participant_token(self):
        with self.app_context():
            for participant in TeraParticipant.query.all():
                self.assertIsNotNone(participant)
                if participant.participant_enabled and participant.participant_token:
                    self.assertIsNotNone(participant.participant_token)
                    self.assertGreater(len(participant.participant_token), 0)
                    response = self._get_with_token_auth(self.test_client, token=participant.participant_token)
                    self.assertEqual(response.status_code, 403)

    def test_get_endpoint_with_static_device_token(self):
        with self.app_context():
            for device in TeraDevice.query.all():
                self.assertIsNotNone(device)
                if device.device_enabled:
                    device_token = device.device_token
                    self.assertIsNotNone(device_token)
                    self.assertGreater(len(device_token), 0)
                    response = self._get_with_token_auth(self.test_client, token=device_token)
                    self.assertEqual(response.status_code, 401)

    def test_get_endpoint_with_service_token_no_params(self):
        with self.app_context():
            service: TeraService = TeraService.get_service_by_key('EmailService')
            self.assertIsNotNone(service)
            service_token = service.get_token(ServiceAccessManager.api_service_token_key)
            self.assertGreater(len(service_token), 0)
            response = self._get_with_token_auth(self.test_client, token=service_token)
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_without_params(self):
        with self.app_context():
            params = {}
            response = self._get_with_token_auth(self.test_client, token=self.user_admin_token, params=params)
            self.assertEqual(response.status_code, 400)

    def test_get_endpoint_invalid_template_id(self):
        with self.app_context():
            params = {'id_template': 100}
            response = self._get_with_token_auth(self.test_client, token=self.user_admin_token, params=params)
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_forbidden_template_id(self):
        with self.app_context():
            template = EmailTemplate.get_template_by_key('SITE_EMAIL')
            self.assertIsNotNone(template)
            params = {'id_template': template.id_email_template}
            response = self._get_with_token_auth(self.test_client, token=self.user_user4_token, params=params)
            self.assertEqual(response.status_code, 403)

            template = EmailTemplate.get_template_by_key('PROJECT_EMAIL')
            self.assertIsNotNone(template)
            params = {'id_template': template.id_email_template}
            response = self._get_with_token_auth(self.test_client, token=self.user_user4_token, params=params)
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_global_template_id(self):
        with self.app_context():
            template = EmailTemplate.get_template_by_key('GENERAL_TEST_EMAIL')
            self.assertIsNotNone(template)
            params = {'id_template': template.id_email_template}
            response = self._get_with_token_auth(self.test_client, token=self.user_user4_token, params=params)
            self.assertEqual(response.status_code, 200)
            self._checkJson(response.json[0])

    def test_get_endpoint_valid_template_id(self):
        with self.app_context():
            template = EmailTemplate.get_template_by_key('SITE_EMAIL')
            self.assertIsNotNone(template)
            params = {'id_template': template.id_email_template}
            response = self._get_with_token_auth(self.test_client, token=self.user_admin_token, params=params)
            self.assertEqual(response.status_code, 200)
            self._checkJson(response.json[0])

            template = EmailTemplate.get_template_by_key('PROJECT_EMAIL')
            self.assertIsNotNone(template)
            params = {'id_template': template.id_email_template}
            response = self._get_with_token_auth(self.test_client, token=self.user_user3_token, params=params)
            self.assertEqual(response.status_code, 200)
            self._checkJson(response.json[0])

    def test_get_endpoint_invalid_template_key(self):
        with self.app_context():
            params = {'key': 'INVALID'}
            response = self._get_with_token_auth(self.test_client, token=self.user_admin_token, params=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 0)

    def test_get_endpoint_forbidden_template_key(self):
        with self.app_context():
            params = {'key': 'SITE_EMAIL'}
            response = self._get_with_token_auth(self.test_client, token=self.user_user4_token, params=params)
            self.assertEqual(response.status_code, 403)

            params = {'key': 'PROJECT_EMAIL'}
            response = self._get_with_token_auth(self.test_client, token=self.user_user4_token, params=params)
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_global_template_key(self):
        with self.app_context():
            params = {'key': 'GENERAL_TEST_EMAIL'}
            response = self._get_with_token_auth(self.test_client, token=self.user_user4_token, params=params)
            self.assertEqual(response.status_code, 200)
            self._checkJson(response.json[0])

    def test_get_endpoint_valid_template_key(self):
        with self.app_context():
            params = {'key': 'PROJECT_EMAIL'}
            response = self._get_with_token_auth(self.test_client, token=self.user_user3_token, params=params)
            self.assertEqual(response.status_code, 200)
            self._checkJson(response.json[0])

            params = {'key': 'SITE_EMAIL'}
            response = self._get_with_token_auth(self.test_client, token=self.user_admin_token, params=params)
            self.assertEqual(response.status_code, 200)
            self._checkJson(response.json[0])

    def test_get_endpoint_invalid_site(self):
        with self.app_context():
            params = {'id_site': 100}
            response = self._get_with_token_auth(self.test_client, token=self.user_admin_token, params=params)
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_forbidden_site(self):
        with self.app_context():
            params = {'id_site': 2}
            response = self._get_with_token_auth(self.test_client, token=self.user_user3_token, params=params)
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_valid_site(self):
        with self.app_context():
            params = {'id_site': 2}
            response = self._get_with_token_auth(self.test_client, token=self.user_admin_token, params=params)
            self.assertEqual(response.status_code, 200)
            templates = EmailTemplate.get_templates_for_site(2)
            self.assertEqual(len(response.json), len(templates))
            for template in response.json:
                self._checkJson(template)

    def test_get_endpoint_invalid_project(self):
        with self.app_context():
            params = {'id_project': 100}
            response = self._get_with_token_auth(self.test_client, token=self.user_admin_token, params=params)
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_forbidden_project(self):
        with self.app_context():
            params = {'id_project': 3}
            response = self._get_with_token_auth(self.test_client, token=self.user_user3_token, params=params)
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_valid_project(self):
        with self.app_context():
            params = {'id_project': 1}
            response = self._get_with_token_auth(self.test_client, token=self.user_user3_token, params=params)
            self.assertEqual(response.status_code, 200)
            templates = EmailTemplate.get_templates_for_project(1)
            self.assertEqual(len(response.json), len(templates))
            for template in response.json:
                self._checkJson(template)

    def test_get_endpoint_key_and_project_no_match(self):
        with self.app_context():
            params = {'id_project': 1, 'key': 'INVALID KEY'}
            response = self._get_with_token_auth(self.test_client, token=self.user_user3_token, params=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 0)

    def test_get_endpoint_key_and_project_match(self):
        with self.app_context():
            params = {'id_project': 1, 'key': 'PROJECT_EMAIL'}
            response = self._get_with_token_auth(self.test_client, token=self.user_user3_token, params=params)
            self.assertEqual(response.status_code, 200)
            templates = EmailTemplate.get_template_by_key('PROJECT_EMAIL', project_id=1)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["id_email_template"], templates.id_email_template)
            self._checkJson(response.json[0])

    def test_get_endpoint_key_and_site_no_match(self):
        with self.app_context():
            params = {'id_site': 1, 'key': 'SITE_EMAIL'}
            response = self._get_with_token_auth(self.test_client, token=self.user_admin_token, params=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 0)

    def test_get_endpoint_key_and_site_match(self):
        with self.app_context():
            params = {'id_site': 2, 'key': 'SITE_EMAIL'}
            response = self._get_with_token_auth(self.test_client, token=self.user_admin_token, params=params)
            self.assertEqual(response.status_code, 200)
            templates = EmailTemplate.get_template_by_key('SITE_EMAIL', site_id=2)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["id_email_template"], templates.id_email_template)
            self._checkJson(response.json[0])

    def _checkJson(self, json_data):
        self.assertGreater(len(json_data), 0)
        self.assertTrue(json_data.__contains__('id_email_template'))
        self.assertTrue(json_data.__contains__('id_site'))
        self.assertTrue(json_data.__contains__('id_project'))
        self.assertTrue(json_data.__contains__('email_template_key'))
        self.assertTrue(json_data.__contains__('email_template'))
        self.assertTrue(json_data.__contains__('email_template_language'))
