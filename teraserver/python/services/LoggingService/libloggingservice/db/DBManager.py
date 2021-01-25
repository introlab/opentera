# Using same base as TeraServer
from services.LoggingService.libloggingservice.db.Base import db

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

        # Apply any database upgrade, if needed
        self.upgrade_db()

    def upgrade_db(self):
        # TODO ALEMBIC UPGRADES...
        pass

    def stamp_db(self):
        # TODO ALEMBIC UPGRADES
        pass

    def store_log_event(self, event: LogEvent):
        entry = LogEntry()
        entry.log_level = event.level
        entry.sender = event.sender
        entry.timestamp = datetime.datetime.fromtimestamp(event.timestamp)
        entry.message = event.message
        db.session.add(entry)
        db.session.commit()
