# Using same base as TeraServer
from opentera.db.Base import BaseModel
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector
from sqlite3 import Connection as SQLite3Connection

# Must include all Database objects here to be properly initialized and created if needed
# All at once to make sure all files are registered.
from services.LoggingService.libloggingservice.db.models.LogEntry import LogEntry
from services.LoggingService.libloggingservice.db.models.LoginEntry import LoginEntry

from services.LoggingService.ConfigManager import ConfigManager
from services.LoggingService.FlaskModule import flask_app
from opentera.messages.python import LogEvent
from opentera.messages.python import LoginEvent

import datetime

# Alembic
from alembic.config import Config
from alembic import command


class DBManager:
    """db_infos = {
        'user': '',
        'pw': '',
        'db': '',
        'host': '',
        'port': '',
        'type': ''
    }"""

    def __init__(self, test: bool = False):
        self.db_uri = None
        self.db = SQLAlchemy()
        self.test = test

    def create_defaults(self, config: ConfigManager, test: bool = False):
        with flask_app.app_context():
            if LogEntry.get_count() == 0:
                entry = LogEntry()
                entry.log_level = LogEvent.LogLevel.LOGLEVEL_INFO
                entry.sender = 'service.LoggingService'
                entry.timestamp = datetime.datetime.now()
                entry.message = 'Database initialized.'
                self.db.session.add(entry)
                self.db.session.commit()

            if test:
                pass

    def open(self, db_infos, echo=False):
        self.db_uri = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % db_infos

        flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': self.db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        self.db.init_app(flask_app)
        self.db.app = flask_app
        BaseModel.set_db(self.db)

        with flask_app.app_context():
            # Init tables
            BaseModel.create_all()

            inspector = Inspector.from_engine(self.db.engine)
            tables = inspector.get_table_names()

            if not tables:
                # New database - stamp with current revision version
                self.stamp_db()
            else:
                # Apply any database upgrade, if needed
                self.upgrade_db()

    def open_local(self, db_infos, echo=False, ram=False):

        if ram:
            self.db_uri = 'sqlite://'
        else:
            self.db_uri = 'sqlite:///%(filename)s' % db_infos

        flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': self.db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        self.db.init_app(flask_app)
        self.db.app = flask_app
        BaseModel.set_db(self.db)

        with flask_app.app_context():
            BaseModel.create_all()

            inspector = Inspector.from_engine(self.db.engine)
            tables = inspector.get_table_names()

            if not tables:
                # New database - stamp with current revision version
                self.stamp_db()
            else:
                # Apply any database upgrade, if needed
                self.upgrade_db()

    def init_alembic(self):
        import sys
        import os
        # determine if application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the pyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app
            # path into variable _MEIPASS'.
            this_file_directory = sys._MEIPASS
            # When frozen, file directory = executable directory
            root_directory = this_file_directory
        else:
            this_file_directory = os.path.dirname(os.path.abspath(__file__))
            root_directory = os.path.join(this_file_directory, '..' + os.sep + '..')

        # this_file_directory = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

        alembic_directory = os.path.join(root_directory, 'alembic')
        ini_path = os.path.join(root_directory, 'alembic.ini')

        # create Alembic config and feed it with paths
        config = Config(ini_path)
        config.set_main_option('script_location', alembic_directory)
        config.set_main_option('sqlalchemy.url', self.db_uri)

        return config

    def upgrade_db(self):
        config = self.init_alembic()

        # prepare and run the command
        revision = 'head'
        sql = False
        tag = None

        # upgrade command
        command.upgrade(config, revision, sql=sql, tag=tag)

    def stamp_db(self):
        config = self.init_alembic()

        # prepare and run the command
        revision = 'head'
        sql = False
        tag = None

        # Stamp database
        command.stamp(config, revision, sql, tag)

    def store_log_event(self, event: LogEvent):
        with flask_app.app_context():
            entry = LogEntry()
            entry.log_level = event.level
            entry.sender = event.sender
            entry.timestamp = datetime.datetime.fromtimestamp(event.timestamp)
            entry.message = event.message
            self.db.session.add(entry)
            self.db.session.commit()

    def store_login_event(self, event: LoginEvent):
        with flask_app.app_context():
            entry = LoginEntry()
            entry.login_timestamp = datetime.datetime.fromtimestamp(event.log_header.timestamp)
            entry.login_log_level = event.log_header.level
            entry.login_sender = event.log_header.sender
            entry.login_user_uuid = event.user_uuid
            entry.login_participant_uuid = event.participant_uuid
            entry.login_device_uuid = event.device_uuid
            entry.login_service_uuid = event.service_uuid
            entry.login_status = event.login_status
            entry.login_type = event.login_type
            entry.login_client_ip = event.client_ip
            entry.login_server_endpoint = event.server_endpoint
            entry.login_client_name = event.client_name
            entry.login_client_version = event.client_version
            entry.login_os_name = event.os_name
            entry.login_os_version = event.os_version
            entry.login_message = event.log_header.message
            self.db.session.add(entry)
            self.db.session.commit()


# Fix foreign_keys on sqlite
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


if __name__ == '__main__':
    config = ConfigManager()
    config.create_defaults()
    manager = DBManager(config)
    manager.open_local({}, echo=True, ram=True)
    manager.create_defaults(config, test=True)
    print('test')

