from BaseLoggingServiceAPITest import BaseLoggingServiceAPITest
from services.LoggingService.FlaskModule import flask_app
from services.LoggingService.libloggingservice.db.models.LoginEntry import LoginEntry

from datetime import datetime
import uuid


class LoggingServiceQueryLoginEntriesTest(BaseLoggingServiceAPITest):
    test_endpoint = '/api/logging/login_entries'

    def setUp(self):
        super().setUp()
        from services.LoggingService.FlaskModule import logging_api_ns
        from BaseLoggingServiceAPITest import FakeFlaskModule
        # Setup minimal API
        from services.LoggingService.API.QueryLoginEntries import QueryLoginEntries
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseLoggingServiceAPITest.getConfig()),
                  'test': True}
        logging_api_ns.add_resource(QueryLoginEntries, '/login_entries', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

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
            from services.LoggingService.Globals import service
            users_uuids = service.get_users_uuids()

            for user_uuid in users_uuids:
                # Create random login entries
                for i in range(50):
                    entry = LoginEntry()
                    entry.login_timestamp = datetime.now()
                    entry.login_log_level = 1
                    entry.login_sender = 'LoggingServiceQueryLoginEntriesTest'
                    entry.login_user_uuid = user_uuid
                    entry.login_participant_uuid = None
                    entry.login_device_uuid = None
                    entry.login_service_uuid = None
                    entry.login_status = 2
                    entry.login_type = 1
                    entry.login_client_ip = '127.0.0.1'
                    entry.login_server_endpoint = '/endpoint'
                    entry.login_client_name = 'client name'
                    entry.login_client_version = 'client version'
                    entry.login_os_name = 'op name'
                    entry.login_os_version = 'os version'
                    entry.login_message = 'random message'
                    LoginEntry.insert(entry)

                token = self._generate_fake_user_token(name='FakeUser', user_uuid=user_uuid,
                                                       superadmin=True, expiration=3600)
                response = self._get_with_service_token_auth(self.test_client, token=token)
                self.assertEqual(response.status_code, 200)

                entries = LoginEntry.query.all()
                self.assertEqual(len(response.json), len(entries))


