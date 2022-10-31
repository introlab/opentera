from flask_sqlalchemy import event, SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector
from sqlite3 import Connection as SQLite3Connection

from twisted.internet import task, reactor
import datetime
import opentera.messages.python as messages

# Must include all Database objects here to be properly initialized and created if needed
from opentera.modules.BaseModule import BaseModule, ModuleNames, create_module_event_topic_from_name

# All at once to make sure all files are registered.
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraDeviceSubType import TeraDeviceSubType
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraDeviceProject import TeraDeviceProject
from opentera.db.models.TeraDeviceSite import TeraDeviceSite
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from opentera.db.models.TeraServerSettings import TeraServerSettings
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSessionEvent import TeraSessionEvent
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServiceRole import TeraServiceRole
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraUserGroup import TeraUserGroup
from opentera.db.models.TeraUserPreference import TeraUserPreference
from opentera.db.models.TeraUserUserGroup import TeraUserUserGroup
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraServiceConfig import TeraServiceConfig
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraTest import TeraTest
from opentera.db.Base import BaseModel

from opentera.config.ConfigManager import ConfigManager
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

        self.db = SQLAlchemy()

        self.db_uri = None

        # Database cleanup task set to run at next midnight
        self.cleanup_database_task = self.start_cleanup_task()

    @staticmethod
    def app_context():
        return flask_app.app_context()

    def start_cleanup_task(self) -> task:
        # Compute time till next midnight
        current_datetime = datetime.datetime.now()
        tomorrow = current_datetime + datetime.timedelta(days=1)
        seconds_to_midnight = (datetime.datetime.combine(tomorrow, datetime.time.min) - current_datetime).seconds

        return task.deferLater(reactor, seconds_to_midnight, self.cleanup_database)
        # return task.deferLater(reactor, 5, self.cleanup_database)

    def setup_events_for_class(self, cls, event_name):
        import json

        @event.listens_for(cls, 'after_update')
        def base_model_updated(mapper, connection, target):
            # print(mapper, connection, target, event_name)
            json_update_event = target.to_json_update_event()
            if json_update_event:
                database_event = messages.DatabaseEvent()
                database_event.type = messages.DatabaseEvent.DB_UPDATE
                database_event.object_type = str(target.get_model_name())
                database_event.object_value = json.dumps(json_update_event)

                event_message = self.create_event_message(
                    create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME, event_name))

                any_message = messages.Any()
                any_message.Pack(database_event)
                event_message.events.append(any_message)
                # Specific topic for each class
                self.publish(event_message.header.topic, event_message.SerializeToString())

        # Send the event before we delete, so we can trace it...
        @event.listens_for(cls, 'after_delete')
        def base_model_deleted(mapper, connection, target):
            # print(mapper, connection, target, event_name)
            json_delete_event = target.to_json_delete_event()
            if json_delete_event:
                database_event = messages.DatabaseEvent()
                database_event.type = messages.DatabaseEvent.DB_DELETE
                database_event.object_type = str(target.get_model_name())
                database_event.object_value = json.dumps(json_delete_event)

                event_message = self.create_event_message(
                    create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME, event_name))

                any_message = messages.Any()
                any_message.Pack(database_event)
                event_message.events.append(any_message)
                # Specific topic for each class
                self.publish(event_message.header.topic, event_message.SerializeToString())

        @event.listens_for(cls, 'after_insert')
        def base_model_inserted(mapper, connection, target):
            # print(mapper, connection, target, event_name)
            json_create_event = target.to_json_create_event()
            if json_create_event:
                database_event = messages.DatabaseEvent()
                database_event.type = messages.DatabaseEvent.DB_CREATE
                database_event.object_type = str(target.get_model_name())
                database_event.object_value = json.dumps(json_create_event)

                event_message = self.create_event_message(
                    create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME, event_name))

                any_message = messages.Any()
                any_message.Pack(database_event)
                event_message.events.append(any_message)
                # Specific topic for each class
                self.publish(event_message.header.topic, event_message.SerializeToString())

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
        access = DBManagerTeraServiceAccess(service=service)
        return access

    def create_defaults(self, config: ConfigManager, test=False):
        if TeraServerSettings.get_count() == 0:
            print('No server settings - creating defaults')
            TeraServerSettings.create_defaults(test)

        if TeraService.get_count() == 0:
            print("No services - creating defaults")
            TeraService.create_defaults(test)

        if TeraServiceRole.get_count() == 0:
            print("No service roles - creating defaults for each service")
            TeraServiceRole.create_defaults(test)

        if TeraSite.get_count() == 0:
            print('No sites - creating defaults')
            TeraSite.create_defaults(test)

        if TeraProject.get_count() == 0:
            print("No projects - creating defaults")
            TeraProject.create_defaults(test)

        if TeraDeviceType.get_count() == 0:
            print('No device types - creating defaults')
            TeraDeviceType.create_defaults(test)

        if TeraServiceProject.get_count() == 0:
            print('No service - project association - creating defaults')
            TeraServiceProject.create_defaults(test)

        if TeraServiceSite.get_count() == 0:
            print('No service - site association - creating defaults')
            TeraServiceSite.create_defaults(test)

        if TeraParticipantGroup.get_count() == 0:
            print("No participant groups - creating defaults")
            TeraParticipantGroup.create_defaults(test)

        if TeraUserGroup.get_count() == 0:
            print("No user groups - creating defaults")
            TeraUserGroup.create_defaults(test)

        if TeraParticipant.get_count() == 0:
            print("No participant - creating defaults")
            TeraParticipant.create_defaults(test)

        if TeraUser.get_count() == 0:
            print('No users - creating defaults')
            TeraUser.create_defaults(test)
            TeraUserUserGroup.create_defaults(test)
            TeraUserPreference.create_defaults(test)

        if TeraDevice.get_count() == 0:
            print('No device - creating defaults')
            TeraDevice.create_defaults(test)
            TeraDeviceProject.create_defaults(test)
            TeraDeviceParticipant.create_defaults(test)
            TeraServiceAccess.create_defaults(test)
            TeraDeviceSubType.create_defaults(test)

        if TeraDeviceSite.get_count() == 0:
            print('No device-site association - creating defaults')
            TeraDeviceSite.create_defaults(test)

        if TeraSessionType.get_count() == 0:
            print("No session type - creating defaults")
            TeraSessionType.create_defaults(test)
            TeraSessionTypeProject.create_defaults(test)

        if TeraSessionTypeSite.get_count() == 0:
            TeraSessionTypeSite.create_defaults(test)

        if TeraSession.get_count() == 0:
            print('No session - creating defaults')
            TeraSession.create_defaults(test)
            TeraSessionEvent.create_defaults(test)
            # TeraAsset.create_defaults(test)

        if TeraAsset.get_count() == 0:
            print('No assets - creating defaults')
            TeraAsset.create_defaults(test)

        if TeraServiceConfig.get_count() == 0:
            print('No service config - creating defaults')
            TeraServiceConfig.create_defaults(test)

        if TeraTestType.get_count() == 0:
            print('No test types - creating defaults')
            TeraTestType.create_defaults(test)
            TeraTestTypeSite.create_defaults(test)
            TeraTestTypeProject.create_defaults(test)

        if TeraTest.get_count() == 0:
            print('No test - creating defaults')
            TeraTest.create_defaults(test)

    def setup_events(self):
        # TODO Add events that need to be sent through redis
        # TODO Useful to specify event name, always get_model_name() ?

        from opentera.db.models import EventNameClassMap
        for name in EventNameClassMap:
            self.setup_events_for_class(EventNameClassMap[name], name)

    def open(self, echo=False):
        self.db_uri = 'postgresql://%(username)s:%(password)s@%(url)s:%(port)s/%(name)s' % self.config.db_config

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
        inspector = Inspector.from_engine(self.db.engine)
        tables = inspector.get_table_names()
        # tables = db.engine.table_names()
        if not tables:
            # Create all tables
            BaseModel.create_all()
            # New database - stamp with current revision version
            self.stamp_db()
        else:
            # Apply any database upgrade, if needed
            self.upgrade_db()

        # Now ready for events
        self.setup_events()

    def open_local(self, db_infos, echo=False, ram=True):
        # self.db_uri = 'sqlite:///%(filename)s' % db_infos

        # IN RAM
        if ram:
            self.db_uri = 'sqlite://'
        else:
            self.db_uri = 'sqlite:///%(filename)s' % db_infos

        flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': self.db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo,
            'SQLALCHEMY_ENGINE_OPTIONS': {}
        })

        # Create db engine
        self.db.init_app(flask_app)
        self.db.app = flask_app
        BaseModel.set_db(self.db)

        # Init tables
        inspector = Inspector.from_engine(self.db.engine)
        tables = inspector.get_table_names()

        if not tables:
            # Create all tables
            BaseModel.create_all()
            # New database - stamp with current revision version
            self.stamp_db()
        else:
            # Apply any database upgrade, if needed
            self.upgrade_db()

        # Now ready for events
        self.setup_events()

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

    def cleanup_database(self):
        print("Cleaning up database...")
        # Updating session states
        TeraSession.cancel_past_not_started_sessions()
        TeraSession.terminate_past_inprogress_sessions()
        # Reschedule cleanup task
        self.cleanup_database_task = self.start_cleanup_task()


# Fix foreign_keys on sqlite
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

# @event.listens_for(db.session, 'after_flush')
# def receive_after_flush(session, flush_context):
#     from modules.Globals import db_man
#     import json
#
#     if db_man:
#         events = list()
#         # Updated objects
#         for obj in session.dirty:
#             # json_update_event = obj.to_json_update_event()
#             # if json_update_event:
#             #     database_event = messages.DatabaseEvent()
#             #     database_event.type = messages.DatabaseEvent.DB_UPDATE
#             #     database_event.object_type = str(obj.get_model_name())
#             #     database_event.object_value = json.dumps(json_update_event)
#             #     events.append(database_event)
#
#             if isinstance(obj, TeraUser):
#                 new_event = messages.UserEvent()
#                 new_event.user_uuid = str(obj.user_uuid)
#                 new_event.type = messages.UserEvent.USER_UPDATED
#                 events.append(new_event)
#
#         # Inserted objects
#         for obj in session.new:
#             # database_event = messages.DatabaseEvent()
#             # database_event.type = messages.DatabaseEvent.DB_CREATE
#             # database_event.object_type = str(obj.get_model_name())
#             # database_event.object_value = json.dumps(obj.to_json())
#             # events.append(database_event)
#
#             if isinstance(obj, TeraUser):
#                 new_event = messages.UserEvent()
#                 new_event.user_uuid = str(obj.user_uuid)
#                 new_event.type = messages.UserEvent.USER_ADDED
#                 events.append(new_event)
#
#         # Deleted objects
#         for obj in session.deleted:
#             # database_event = messages.DatabaseEvent()
#             # database_event.type = messages.DatabaseEvent.DB_DELETE
#             # database_event.object_type = str(obj.get_model_name())
#             # database_event.object_value = json.dumps(obj.to_json())
#             # events.append(database_event)
#
#             if isinstance(obj, TeraUser):
#                 new_event = messages.UserEvent()
#                 new_event.user_uuid = str(obj.user_uuid)
#                 new_event.type = messages.UserEvent.USER_DELETED
#                 events.append(new_event)
#
#         # Create event message
#         if len(events) > 0:
#             tera_message = db_man.create_event_message(
#                 create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME))
#             any_events = list()
#             for db_event in events:
#                 any_message = messages.Any()
#                 any_message.Pack(db_event)
#                 tera_message.events.append(any_message)
#
#             db_man.publish(create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME),
#                            tera_message.SerializeToString())

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


if __name__ == '__main__':
    with flask_app.app_context():
        config = ConfigManager()
        config.create_defaults()
        manager = DBManager(config)
        print(manager)
        manager.open_local(dict(), echo=True, ram=True)
        user = TeraUser()
        user.query.all()
        test = TeraUser.query.all()
        manager.create_defaults(config, test=True)

