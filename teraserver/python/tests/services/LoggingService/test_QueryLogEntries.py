from BaseLoggingServiceAPITest import BaseLoggingServiceAPITest
from services.LoggingService.libloggingservice.db.models.LogEntry import LogEntry
from datetime import datetime, timedelta


class LoggingServiceQueryLogEntriesTest(BaseLoggingServiceAPITest):
    test_endpoint = '/api/logging/log_entries'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_with_invalid_token(self):
        with BaseLoggingServiceAPITest.app_context():
            response = self._get_with_service_token_auth(self.test_client, token="invalid")
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_with_valid_token_but_not_admin(self):
        with BaseLoggingServiceAPITest.app_context():
            token = self._generate_fake_user_token(name='FakeUser', superadmin=False, expiration=3600)
            response = self._get_with_service_token_auth(self.test_client, token=token)
            self.assertEqual(response.status_code, 403)

    def test_get_endpoint_with_valid_token_and_admin(self):
        with BaseLoggingServiceAPITest.app_context():
            token = self._generate_fake_user_token(name='FakeUser', superadmin=True, expiration=3600)

            all_entries = []
            for i in range(50):
                current_time = datetime.now()
                entry = self._create_log_entry(current_time, 1, 'test', 'test_message')
                self.assertIsNotNone(entry)
                LogEntry.insert(entry)
                self.assertIsNotNone(entry.id_log_entry)
                all_entries.append(entry)

            response = self._get_with_service_token_auth(self.test_client, token=token)
            self.assertEqual(response.status_code, 200)
            self.assertGreaterEqual(len(response.json), 50)

            # Cleanup
            for entry in all_entries:
                LogEntry.delete(entry.id_log_entry)

    def test_get_endpoint_with_valid_token_and_admin_with_start_end_dates(self):
        with BaseLoggingServiceAPITest.app_context():
            token = self._generate_fake_user_token(name='FakeUser', superadmin=True, expiration=3600)
            # Make sure everything is in the future, so we can filter with known dates
            all_entries = []
            current_time = datetime.now() + timedelta(hours=1)
            tomorrow = current_time + timedelta(days=1)

            for i in range(50):
                entry = self._create_log_entry(current_time, 1, 'test', 'test_message')
                self.assertIsNotNone(entry)
                LogEntry.insert(entry)
                self.assertIsNotNone(entry.id_log_entry)
                all_entries.append(entry)

            for i in range(50):
                entry = self._create_log_entry(tomorrow, 1, 'test', 'test_message')
                self.assertIsNotNone(entry)
                LogEntry.insert(entry)
                self.assertIsNotNone(entry.id_log_entry)
                all_entries.append(entry)

            params = {
                'start_date': str(current_time.isoformat()),
                'end_date': str(current_time.isoformat())
            }

            response = self._get_with_service_token_auth(self.test_client, token=token, params=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 50)

            params['end_date'] = str(tomorrow.isoformat())
            response = self._get_with_service_token_auth(self.test_client, token=token, params=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 100)

            # Cleanup
            for entry in all_entries:
                LogEntry.delete(entry.id_log_entry)

    def test_get_endpoint_with_valid_token_and_admin_with_offset(self):
        with BaseLoggingServiceAPITest.app_context():
            token = self._generate_fake_user_token(name='FakeUser', superadmin=True, expiration=3600)

            all_entries = []
            current_time = datetime.now()

            for i in range(50):
                entry = self._create_log_entry(current_time, 1, 'test', 'test_message')
                self.assertIsNotNone(entry)
                LogEntry.insert(entry)
                self.assertIsNotNone(entry.id_log_entry)
                all_entries.append(entry)

            params = {
                'offset': 10,
            }

            response = self._get_with_service_token_auth(self.test_client, token=token, params=params)
            self.assertEqual(response.status_code, 200)
            self.assertLess(len(response.json), 50)

            # Cleanup
            for entry in all_entries:
                LogEntry.delete(entry.id_log_entry)

    def test_get_endpoint_with_valid_token_and_admin_with_limit(self):
        with BaseLoggingServiceAPITest.app_context():
            token = self._generate_fake_user_token(name='FakeUser', superadmin=True, expiration=3600)

            all_entries = []
            current_time = datetime.now()
            yesterday = current_time - timedelta(days=1)

            for i in range(50):
                entry = self._create_log_entry(yesterday, 1, 'test', 'test_message')
                self.assertIsNotNone(entry)
                LogEntry.insert(entry)
                self.assertIsNotNone(entry.id_log_entry)
                all_entries.append(entry)

            params = {
                'limit': 10,
            }

            response = self._get_with_service_token_auth(self.test_client, token=token, params=params)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 10)

            # Cleanup
            for entry in all_entries:
                LogEntry.delete(entry.id_log_entry)

    def test_get_endpoint_with_valid_token_and_admin_and_log_level(self):
        with BaseLoggingServiceAPITest.app_context():
            token = self._generate_fake_user_token(name='FakeUser', superadmin=True, expiration=3600)

            all_entries = []
            min_timestamp = ''
            max_timestamp = ''
            for i in range(50):
                current_time = datetime.now()
                entry = self._create_log_entry(current_time, 99, 'test', 'test_message')
                self.assertIsNotNone(entry)
                LogEntry.insert(entry)
                self.assertIsNotNone(entry.id_log_entry)
                all_entries.append(entry)

            # Filter with higher log level should give no entry
            response = self._get_with_service_token_auth(self.test_client, token=token, params={'log_level': 1})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 0)

            # Filter with exact log level should give at least amount
            response = self._get_with_service_token_auth(self.test_client, token=token, params={'log_level': 99})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 50)

            # Cleanup
            for entry in all_entries:
                LogEntry.delete(entry.id_log_entry)

    def test_get_endpoint_stats_with_valid_token_and_admin(self):
        with BaseLoggingServiceAPITest.app_context():
            token = self._generate_fake_user_token(name='FakeUser', superadmin=True, expiration=3600)

            all_entries = []
            min_timestamp = ''
            max_timestamp = ''
            for i in range(50):
                current_time = datetime.now()
                if i == 0:
                    min_timestamp = current_time.isoformat()
                if i == 49:
                    max_timestamp = current_time.isoformat()
                entry = self._create_log_entry(current_time, 1, 'test', 'test_message')
                self.assertIsNotNone(entry)
                LogEntry.insert(entry)
                self.assertIsNotNone(entry.id_log_entry)
                all_entries.append(entry)

            response = self._get_with_service_token_auth(self.test_client, token=token, params={'stats': True})
            self.assertEqual(response.status_code, 200)
            self.assertTrue('count' in response.json)
            self.assertGreaterEqual(response.json['count'], 51)
            self.assertTrue('min_timestamp' in response.json)
            self.assertLessEqual(response.json['min_timestamp'], min_timestamp)
            self.assertTrue('max_timestamp' in response.json)
            self.assertEqual(response.json['max_timestamp'], max_timestamp)

            # Cleanup
            for entry in all_entries:
                LogEntry.delete(entry.id_log_entry)

    def _create_log_entry(self, timestamp: datetime, log_level: int, sender: str, message: str):
        self.assertIsNotNone(timestamp)
        self.assertIsNotNone(log_level)
        self.assertIsNotNone(sender)
        self.assertIsNotNone(message)

        entry = LogEntry()
        entry.timestamp = timestamp
        entry.log_level = log_level
        entry.sender = sender
        entry.message = message
        return entry
