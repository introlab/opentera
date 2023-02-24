import unittest
from datetime import datetime
from services.LoggingService.libloggingservice.db.DBManager import DBManager
from services.LoggingService.ConfigManager import ConfigManager
from services.LoggingService.libloggingservice.db.models.LogEntry import LogEntry
from services.LoggingService.libloggingservice.db.models.LoginEntry import LoginEntry
import uuid
from flask import Flask


class LoggingServiceDBManagerTest(unittest.TestCase):
    def setUp(self):
        self.flask_app = Flask('LoggingServiceDBManagerTest')
        with self.flask_app.app_context():
            self.config = ConfigManager()
            self.config.create_defaults()
            self.dbman = DBManager(app=self.flask_app, test=True)
            self.dbman.open_local({}, False, True)
            self.dbman.create_defaults(self.config, test=True)

    def tearDown(self):
        with self.flask_app.app_context():
            self.dbman.db.session.rollback()

    def test_create_defaults_should_create_one_log_entry_and_no_login_entry(self):
        with self.flask_app.app_context():
            log_entries = LogEntry.query.all()
            self.assertEqual(len(log_entries), 1)
            login_entries = LoginEntry.query.all()
            self.assertEqual(len(login_entries), 0)

    def test_insert_update_delete_log_entry(self):
        with self.flask_app.app_context():
            entry = LogEntry()
            entry.log_level = 1
            entry.sender = 'test_insert_log_entry'
            entry.message = 'test message'
            entry.timestamp = datetime.now()
            # Insert
            LogEntry.insert(entry)
            self.assertGreater(entry.id_log_entry, 1)
            # Update
            LogEntry.update(entry.id_log_entry, {'message': 'updated test message'})
            entry2 = LogEntry.get_log_entry_by_id(entry.id_log_entry)
            self.assertIsNotNone(entry2)
            self.assertEqual(entry.message, entry2.message)
            self.assertEqual(entry.id_log_entry, entry2.id_log_entry)
            # Delete
            LogEntry.delete(entry.id_log_entry)
            self.assertIsNone(LogEntry.get_log_entry_by_id(entry.id_log_entry))

    def test_insert_update_delete_login_entry(self):
        with self.flask_app.app_context():
            login_entry = LoginEntry()
            login_entry.login_timestamp = datetime.now()
            login_entry.login_log_level = 1
            login_entry.login_sender = 'test_insert_update_delete_login_entry'
            login_entry.login_user_uuid = str(uuid.uuid4())
            login_entry.login_status = 0
            login_entry.login_type = 0
            login_entry.login_client_ip = 'localhost'
            login_entry.login_message = 'test login message'
            # Insert
            LoginEntry.insert(login_entry)
            self.assertIsNotNone(login_entry.id_login_event)
            # Update
            LoginEntry.update(login_entry.id_login_event, {'login_message': 'updated login message'})
            login_entry_2 = LoginEntry.get_login_entry_by_id(login_entry.id_login_event)
            self.assertEqual(login_entry.login_message, login_entry_2.login_message)
            self.assertEqual(login_entry.id_login_event, login_entry_2.id_login_event)
            # Delete
            LoginEntry.delete(login_entry.id_login_event)
            self.assertIsNone(LoginEntry.get_login_entry_by_id(login_entry.id_login_event))
