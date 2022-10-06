# Using same base as TeraServer
from services.LoggingService.libloggingservice.db.Base import db
from sqlalchemy.engine.reflection import Inspector

# Must include all Database objects here to be properly initialized and created if needed
# All at once to make sure all files are registered.
from services.LoggingService.libloggingservice.db.models.LogEntry import LogEntry

from services.LoggingService.ConfigManager import ConfigManager
from services.LoggingService.FlaskModule import flask_app
from opentera.messages.python.LogEvent_pb2 import LogEvent
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

    def __init__(self):
        self.db_uri = None

    def create_defaults(self, config: ConfigManager):
        if LogEntry.get_count() == 0:
            entry = LogEntry()
            entry.log_level = LogEvent.LogLevel.LOGLEVEL_INFO
            entry.sender = 'service.LoggingService'
            entry.timestamp = datetime.datetime.now()
            entry.message = 'Database initialized.'
            db.session.add(entry)
            db.session.commit()

    def open(self, db_infos, echo=False):
        self.db_uri = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % db_infos

        flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': self.db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        db.init_app(flask_app)
        db.app = flask_app

        # Init tables
        # db.drop_all()
        db.create_all()

        inspector = Inspector.from_engine(db.engine)
        tables = inspector.get_table_names()
        # tables = db.engine.table_names()
        if not tables:
            # Create all tables
            db.create_all()
            # New database - stamp with current revision version
            self.stamp_db()
        else:
            # Apply any database upgrade, if needed
            self.upgrade_db()

    def open_local(self, db_infos, echo=False):
        self.db_uri = 'sqlite:///%(filename)s' % db_infos

        flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': self.db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        db.init_app(flask_app)
        db.app = flask_app

        # db.drop_all()
        db.create_all()

        inspector = Inspector.from_engine(db.engine)
        tables = inspector.get_table_names()
        # tables = db.engine.table_names()
        if not tables:
            # Create all tables
            db.create_all()
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
        entry = LogEntry()
        entry.log_level = event.level
        entry.sender = event.sender
        entry.timestamp = datetime.datetime.fromtimestamp(event.timestamp)
        entry.message = event.message
        db.session.add(entry)
        db.session.commit()
