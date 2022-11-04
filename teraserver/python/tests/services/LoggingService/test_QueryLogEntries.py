from BaseLoggingServiceAPITest import BaseLoggingServiceAPITest
from services.LoggingService.FlaskModule import flask_app


class LoggingServiceQueryLogEntriesTest(BaseLoggingServiceAPITest):
    test_endpoint = '/api/logging/log_entries'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_with_invalid_token(self):
        with flask_app.app_context():
            response = self._get_with_service_token_auth(self.test_client, token="invalid")
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_with_valid_token_but_not_admin(self):
        with flask_app.app_context():
            token = self._generate_fake_user_token(name='FakeUser', superadmin=False, expiration=3600)
            response = self._get_with_service_token_auth(self.test_client, token=token)
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_with_valid_token_and_admin(self):
        with flask_app.app_context():
            token = self._generate_fake_user_token(name='FakeUser', superadmin=True, expiration=3600)
            response = self._get_with_service_token_auth(self.test_client, token=token)
            self.assertEqual(response.status_code, 200)

