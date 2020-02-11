from libtera.db.Base import db

# Must include all Database objects here to be properly initialized and created if needed


# All at once to make sure all files ar registered.
from libtera.db.models import *

from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.models.TeraDeviceType import TeraDeviceType
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraSession import TeraSession
from libtera.db.models.TeraSessionType import TeraSessionType
from libtera.db.models.TeraDeviceData import TeraDeviceData
from libtera.db.models.TeraDeviceSite import TeraDeviceSite
from libtera.db.models.TeraDeviceProject import TeraDeviceProject
from libtera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from libtera.db.models.TeraSessionTypeDeviceType import TeraSessionTypeDeviceType
from libtera.db.models.TeraServerSettings import TeraServerSettings
from libtera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from libtera.db.models.TeraSessionEvent import TeraSessionEvent

from libtera.ConfigManager import ConfigManager

from modules.FlaskModule.FlaskModule import flask_app

# User access with roles
from .DBManagerTeraUserAccess import DBManagerTeraUserAccess
from .DBManagerTeraDeviceAccess import DBManagerTeraDeviceAccess

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

    @staticmethod
    def userAccess(user: TeraUser):
        access = DBManagerTeraUserAccess(user=user)
        return access

    @staticmethod
    def deviceAccess(device: TeraDevice):
        access = DBManagerTeraDeviceAccess(device=device)
        return access

    def create_defaults(self, config: ConfigManager):
        if TeraServerSettings.get_count() == 0:
            print('No server settings - creating defaults')
            TeraServerSettings.create_defaults()

        if TeraSite.get_count() == 0:
            print('No sites - creating defaults')
            TeraSite.create_defaults()

        if TeraProject.get_count() == 0:
            print("No projects - creating defaults")
            TeraProject.create_defaults()

        if TeraParticipantGroup.get_count() == 0:
            print("No participant groups - creating defaults")
            TeraParticipantGroup.create_defaults()

        if TeraParticipant.get_count() == 0:
            print("No participant - creating defaults")
            TeraParticipant.create_defaults()

        if TeraUser.get_count() == 0:
            print('No users - creating defaults')
            TeraUser.create_defaults()

        if TeraDeviceType.get_count() == 0:
            print('No device types - creating defaults')
            TeraDeviceType.create_defaults()

        if TeraDevice.get_count() == 0:
            print('No device - creating defaults')
            TeraDevice.create_defaults()
            TeraDeviceSite.create_defaults()
            TeraDeviceProject.create_defaults()
            TeraDeviceParticipant.create_defaults()

        if TeraSessionType.get_count() == 0:
            print("No session type - creating defaults")
            TeraSessionType.create_defaults()
            TeraSessionTypeDeviceType.create_defaults()
            TeraSessionTypeProject.create_defaults()

        if TeraSession.get_count() == 0:
            print('No session - creating defaults')
            TeraSession.create_defaults()
            TeraDeviceData.create_defaults(config.server_config['upload_path'])
            TeraSessionEvent.create_defaults()

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

        # Init tables
        db.create_all()

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
