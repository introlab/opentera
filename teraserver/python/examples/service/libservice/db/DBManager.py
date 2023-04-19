from libservice.db.models.BaseModel import BaseModel

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.engine.reflection import Inspector

# Must include all Database objects here to be properly initialized and created if needed

from ConfigManager import ConfigManager
from FlaskModule import flask_app

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

    def __init__(self, app=flask_app, test: bool = False):
        self.db_uri = None
        self.db = SQLAlchemy()
        self.app = app
        self.test = test

    def create_defaults(self, config: ConfigManager):
        pass

    def open(self, db_infos, echo=False):
        self.db_uri = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % db_infos

        self.app.config.update({
            'SQLALCHEMY_DATABASE_URI': self.db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        self.db.init_app(self.app)
        self.db.app = self.app

        BaseModel.set_db(self.db)

        with self.app.app_context():
            BaseModel.create_all()

            inspector = Inspector.from_engine(self.db.engine)
            tables = inspector.get_table_names()

            if not tables:
                # New database - stamp with current revision version
                self.stamp_db()
            else:
                # Apply any database upgrade, if needed
                self.upgrade_db()

    def open_local(self, db_infos, echo=False):
        self.db_uri = 'sqlite://'

        self.app.config.update({
            'SQLALCHEMY_DATABASE_URI': self.db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        self.db.init_app(self.app)
        self.db.app = self.app
        BaseModel.set_db(self.db)

        with self.app.app_context():
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
        alembic_config = Config(ini_path)
        alembic_config.set_main_option('script_location', alembic_directory)
        alembic_config.set_main_option('sqlalchemy.url', self.db_uri)

        return alembic_config

    def upgrade_db(self):
        alembic_config = self.init_alembic()

        # prepare and run the command
        revision = 'head'
        sql = False
        tag = None

        # upgrade command
        command.upgrade(alembic_config, revision, sql=sql, tag=tag)

    def stamp_db(self):
        alembic_config = self.init_alembic()

        # prepare and run the command
        revision = 'head'
        sql = False
        tag = None

        # Stamp database
        command.stamp(alembic_config, revision, sql, tag)


if __name__ == '__main__':
    config = ConfigManager()
    config.create_defaults()
    manager = DBManager()
    manager.open_local({}, echo=True)
    manager.create_defaults(config)
