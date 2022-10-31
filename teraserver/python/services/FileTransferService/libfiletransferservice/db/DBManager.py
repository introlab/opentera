# Using same base as TeraServer
from opentera.db.Base import BaseModel
from flask_sqlalchemy import SQLAlchemy

# Must include all Database objects here to be properly initialized and created if needed
# All at once to make sure all files are registered.
import services.FileTransferService.libfiletransferservice.db.models

from services.FileTransferService.ConfigManager import ConfigManager
from services.FileTransferService.FlaskModule import flask_app
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
        self.db = SQLAlchemy()
        self.db_uri = None

    def create_defaults(self, config: ConfigManager):
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

        # Init tables
        BaseModel.create_all()

        # Apply any database upgrade, if needed
        self.upgrade_db()

    def open_local(self, db_infos, echo=False):
        self.db_uri = 'sqlite://'

        flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': self.db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        self.db.init_app(flask_app)
        self.db.app = flask_app
        BaseModel.set_db(self.db)

        # Init tables
        BaseModel.create_all()

        # Apply any database upgrade, if needed
        self.upgrade_db()

    def upgrade_db(self):
        # TODO ALEMBIC UPGRADES...
        pass

    def stamp_db(self):
        # TODO ALEMBIC UPGRADES
        pass


if __name__ == '__main__':
    config = ConfigManager()
    config.create_defaults()
    manager = DBManager()
    manager.open_local({}, echo=True)
    manager.create_defaults(config)
    print('test')
