from flask_sqlalchemy import event
from libtera.db.Base import db
import messages.python as messages

# Must include all Database objects here to be properly initialized and created if needed
from modules.BaseModule import BaseModule, ModuleNames, create_module_event_topic_from_name

# All at once to make sure all files ar registered.

from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.models.TeraDeviceType import TeraDeviceType
from libtera.db.models.TeraDeviceSubType import TeraDeviceSubType
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraSession import TeraSession
from libtera.db.models.TeraSessionType import TeraSessionType
from libtera.db.models.TeraDeviceData import TeraDeviceData
from libtera.db.models.TeraDeviceProject import TeraDeviceProject
from libtera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from libtera.db.models.TeraSessionTypeDeviceType import TeraSessionTypeDeviceType
from libtera.db.models.TeraServerSettings import TeraServerSettings
from libtera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from libtera.db.models.TeraSessionEvent import TeraSessionEvent
from libtera.db.models.TeraAsset import TeraAsset
from libtera.db.models.TeraService import TeraService
from libtera.db.models.TeraServiceRole import TeraServiceRole
from libtera.db.models.TeraServiceProject import TeraServiceProject
from libtera.db.models.TeraUserGroup import TeraUserGroup

from libtera.ConfigManager import ConfigManager

from modules.FlaskModule.FlaskModule import flask_app

# User access with roles
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from modules.DatabaseModule.DBManagerTeraDeviceAccess import DBManagerTeraDeviceAccess
from modules.DatabaseModule.DBManagerTeraParticipantAccess import DBManagerTeraParticipantAccess
from modules.DatabaseModule.DBManagerTeraServiceAccess import DBManagerTeraServiceAccess

# Alembic
from alembic.config import Config
from alembic import command


class DBManager (BaseModule):
    """db_infos = {
        'user': '',
        'pw': '',
        'db': '',
        'host': '',
        'port': '',
        'type': ''
    }"""

    def __init__(self, config: ConfigManager):

        BaseModule.__init__(self, ModuleNames.DATABASE_MODULE_NAME.value, config)

        self.db_uri = None

    @staticmethod
    def userAccess(user: TeraUser):
        access = DBManagerTeraUserAccess(user=user)
        return access

    @staticmethod
    def deviceAccess(device: TeraDevice):
        access = DBManagerTeraDeviceAccess(device=device)
        return access

    @staticmethod
    def participantAccess(participant: TeraParticipant):
        access = DBManagerTeraParticipantAccess(participant=participant)
        return access

    @staticmethod
    def serviceAccess(service: TeraService):
        access = DBManagerTeraServiceAccess(service = service)
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

        if TeraService.get_count() == 0:
            print("No services - creating defaults")
            TeraService.create_defaults()

        if TeraServiceRole.get_count() == 0:
            print("No service roles - creating defaults for each service")
            TeraServiceRole.create_defaults()

        if TeraServiceProject.get_count() == 0:
            print('No service - project association - creating defaults')
            TeraServiceProject.create_defaults()

        if TeraParticipantGroup.get_count() == 0:
            print("No participant groups - creating defaults")
            TeraParticipantGroup.create_defaults()

        if TeraUserGroup.get_count() == 0:
            print("No user groups - creating defaults")
            TeraUserGroup.create_defaults()

        if TeraParticipant.get_count() == 0:
            print("No participant - creating defaults")
            TeraParticipant.create_defaults()

        if TeraUser.get_count() == 0:
            print('No users - creating defaults')
            TeraUser.create_defaults()

        if TeraDeviceType.get_count() == 0:
            print('No device types - creating defaults')
            TeraDeviceType.create_defaults()

        if TeraDeviceSubType.get_count() == 0:
            print("No device sub types - creating defaults")
            TeraDeviceSubType.create_defaults()

        if TeraDevice.get_count() == 0:
            print('No device - creating defaults')
            TeraDevice.create_defaults()
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
            # TeraAsset.create_defaults()

        if TeraAsset.get_count() == 0:
            print('No assets - creating defaults')
            TeraAsset.create_defaults()

    def open(self, echo=False):
        # self.db_uri = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % db_infos
        self.db_uri = 'postgresql://%(username)s:%(password)s@%(url)s:%(port)s/%(name)s' % self.config.db_config

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


@event.listens_for(db.session, 'after_flush')
def receive_after_flush(session, flush_context):
    from modules.Globals import db_man

    if db_man:
        events = list()

        # Updated objects
        for obj in session.dirty:
            if isinstance(obj, TeraUser):
                new_event = messages.UserEvent()
                new_event.user_uuid = str(obj.user_uuid)
                new_event.type = messages.UserEvent.USER_UPDATED
                events.append(new_event)

        # Inserted objects
        for obj in session.new:
            if isinstance(obj, TeraUser):
                new_event = messages.UserEvent()
                new_event.user_uuid = str(obj.user_uuid)
                new_event.type = messages.UserEvent.USER_ADDED
                events.append(new_event)

        # Deleted objects
        for obj in session.deleted:
            if isinstance(obj, TeraUser):
                new_event = messages.UserEvent()
                new_event.user_uuid = str(obj.user_uuid)
                new_event.type = messages.UserEvent.USER_DELETED
                events.append(new_event)

        # Create event message
        if len(events) > 0:
            tera_message = db_man.create_event_message(
                create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME))
            any_events = list()
            for db_event in events:
                any_message = messages.Any()
                any_message.Pack(db_event)
                tera_message.events.append(any_message)
            db_man.publish(create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME),
                           tera_message.SerializeToString())


# @event.listens_for(TeraUser, 'after_update')
# def user_updated(mapper, connection, target):
#     from modules.Globals import db_man
#     # Publish event message
#     # Advertise that we have a new user
#     tera_message = db_man.create_event_message(create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME))
#     user_event = messages.UserEvent()
#     user_event.user_uuid = str(target.user_uuid)
#     user_event.type = messages.UserEvent.USER_UPDATED
#     # Need to use Any container
#     any_message = messages.Any()
#     any_message.Pack(user_event)
#     tera_message.events.extend([any_message])
#
#     # Publish
#     db_man.publish(create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME),
#                    tera_message.SerializeToString())
