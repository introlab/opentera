from sqlite3 import Connection as SQLite3Connection
import datetime
import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, inspect, update
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector
from twisted.internet import task, reactor
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
# from opentera.db.models.TeraSessionDevices import TeraSessionDevices
from opentera.db.Base import BaseModel
from opentera.db.models import EventNameClassMap


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

    def __init__(self, config: ConfigManager, app=flask_app):

        BaseModule.__init__(self, ModuleNames.DATABASE_MODULE_NAME.value, config)

        # Future parameters = use only SQLALchemy 2.x features
        self.db = SQLAlchemy(engine_options={'future': True}, session_options={'future': True})
        self.db_uri = None
        self.app = app
        self.db_in_ram = False

        # Database cleanup task set to run at next midnight
        self.cleanup_database_task = self.start_cleanup_task()

    def start_cleanup_task(self) -> task:
        # Compute time till next midnight
        current_datetime = datetime.datetime.now()
        tomorrow = current_datetime + datetime.timedelta(days=1)
        seconds_to_midnight = (datetime.datetime.combine(tomorrow, datetime.time.min) - current_datetime).seconds

        return task.deferLater(reactor, seconds_to_midnight, self.cleanup_database)
        # return task.deferLater(reactor, 5, self.cleanup_database)

    def setup_events_for_2fa_sites(self) -> None:
        """
        We need to validate that 2FA is enabled for all users in the site when the flag is set.
        This can occur on multiple occasions : when the site is created, updated and also when user
        groups are modified.
        """
        @event.listens_for(TeraSite, 'after_update')
        @event.listens_for(TeraSite, 'after_insert')
        def site_updated_or_inserted(mapper, connection, target: TeraSite):
            # Check if 2FA is enabled for this site
            if target and target.site_2fa_required:
                # Get all users that have access to this site
                users = TeraServiceAccess.query.join(TeraServiceRole, TeraServiceAccess.id_service_role == TeraServiceRole.id_service_role) \
                    .join(TeraUserUserGroup, TeraServiceAccess.id_user_group == TeraUserUserGroup.id_user_group) \
                    .join(TeraUser, TeraUserUserGroup.id_user == TeraUser.id_user) \
                    .join(TeraSite, TeraServiceRole.id_site == TeraSite.id_site) \
                    .filter(TeraSite.id_site == target.id_site) \
                    .with_entities(TeraUser).all()  # Return the user information only

                # Enable 2FA for all standard users found
                for user in users:
                    connection.execute(
                        update(TeraUser)
                        .where(TeraUser.id_user == user.id_user)
                        .values(user_2fa_enabled=True)
                    )

                # Enable 2FA for all superadmins
                connection.execute(
                    update(TeraUser)
                    .where(TeraUser.user_superadmin == bool(True))
                    .values(user_2fa_enabled=True)
                )

        @event.listens_for(TeraUserGroup, 'after_update')
        @event.listens_for(TeraUserGroup, 'after_insert')
        def user_group_updated_or_inserted(mapper, connection, target: TeraUserGroup):

            # Check if 2FA is enabled for a related site in a single sql query
            if target:
                # Get users from the group that have access to a site with 2FA enabled
                users = TeraUser.query.join(TeraUserUserGroup, TeraUser.id_user == TeraUserUserGroup.id_user) \
                    .join(TeraServiceAccess, TeraUserUserGroup.id_user_group == TeraServiceAccess.id_user_group) \
                    .join(TeraServiceRole, TeraServiceAccess.id_service_role == TeraServiceRole.id_service_role) \
                    .join(TeraSite, TeraServiceRole.id_site == TeraSite.id_site) \
                    .filter(TeraUserUserGroup.id_user_group == target.id_user_group) \
                    .filter(TeraSite.site_2fa_required == bool(True)) \
                    .with_entities(TeraUser).all()  # Return the user information only

                # Enable 2FA for all users found
                for user in users:
                    connection.execute(
                        update(TeraUser)
                        .where(TeraUser.id_user == user.id_user)
                        .values(user_2fa_enabled=True)
                    )

        @event.listens_for(TeraUserUserGroup, 'after_update')
        @event.listens_for(TeraUserUserGroup, 'after_insert')
        def user_user_group_updated_or_inserted(mapper, connection, target: TeraUserUserGroup):
            # If the user in the usergroup has access to a site with 2FA enabled, enable 2FA for the user
            if target:
                sites = TeraServiceAccess.query.join(TeraServiceRole, TeraServiceAccess.id_service_role ==
                                                     TeraServiceRole.id_service_role) \
                                                        .join(TeraSite, TeraServiceRole.id_site == TeraSite.id_site) \
                                                        .filter(TeraServiceAccess.id_user_group == target.id_user_group) \
                                                        .with_entities(TeraSite).all()  # Return the site information only

                for site in sites:
                    if site.site_2fa_required:
                        # Perform single update for user
                        connection.execute(
                            update(TeraUser)
                            .where(TeraUser.id_user == target.id_user)
                            .values(user_2fa_enabled=True)
                        )
                        break

        @event.listens_for(TeraUser, 'after_update')
        @event.listens_for(TeraUser, 'after_insert')
        def user_updated_or_inserted(mapper, connection, target: TeraUser):
            # Check if 2FA is enabled for a related site through user groups
            if target:
                sites = []
                if target.user_superadmin:
                    # Superadmin has access to all sites, so we need to verify if any of them have 2FA enabled
                    sites = TeraSite.query.filter(TeraSite.site_2fa_required == bool(True)).all()
                else:
                    # Standard user need to verify sites through user groups
                    sites = TeraServiceAccess.query.join(TeraUserUserGroup, TeraServiceAccess.id_user_group == TeraUserUserGroup.id_user_group) \
                                                            .join(TeraServiceRole, TeraServiceAccess.id_service_role == TeraServiceRole.id_service_role) \
                                                            .join(TeraSite, TeraServiceRole.id_site == TeraSite.id_site) \
                                                            .filter(TeraUserUserGroup.id_user == target.id_user) \
                                                            .with_entities(TeraSite).all()  # Return the site information only

                if not sites:
                    # User is not in any user group related to a 2FA site
                    # If 2FA is disabled, make sure other 2FA fields are reset
                    if not target.user_2fa_enabled:
                        connection.execute(
                            update(TeraUser)
                            .where(TeraUser.id_user == target.id_user)
                            .values(
                                user_2fa_otp_enabled=False,
                                user_2fa_otp_secret=None,
                                user_2fa_email_enabled=False
                            )
                        )
                else:
                    for site in sites:
                        if site.site_2fa_required:
                            # Perform single update for user
                            connection.execute(
                                update(TeraUser)
                                .where(TeraUser.id_user == target.id_user)
                                .values(user_2fa_enabled=True)
                            )
                            break


    def setup_events_for_class(self, cls, event_name):
        """
        Setup events for a specific class. This will allow to send events through redis when a specific
        event occurs on a specific class. This is useful to trace changes in the database.
        The list of classes that produce events is defined in the EventNameClassMap in opentera/db/models/__init__.py.
        :param cls: Class to setup events for
        :param event_name: Name of the event
        """

        @event.listens_for(cls, 'after_update')
        def base_model_updated(mapper, connection, target):
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
    def userAccess(user: TeraUser) -> DBManagerTeraUserAccess:
        access = DBManagerTeraUserAccess(user=user)
        return access

    @staticmethod
    def deviceAccess(device: TeraDevice) -> DBManagerTeraDeviceAccess:
        access = DBManagerTeraDeviceAccess(device=device)
        return access

    @staticmethod
    def participantAccess(participant: TeraParticipant) -> DBManagerTeraParticipantAccess:
        access = DBManagerTeraParticipantAccess(participant=participant)
        return access

    @staticmethod
    def serviceAccess(service: TeraService) -> DBManagerTeraServiceAccess:
        access = DBManagerTeraServiceAccess(service=service)
        return access

    def create_defaults(self, config: ConfigManager, test=False):
        with self.app.app_context():
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
        """
        Called after the database is opened. This will setup events for all classes that need to be monitored.
        """
        for event_name, model_class in EventNameClassMap.items():
            self.setup_events_for_class(model_class, event_name)

        # Setup events for 2FA sites
        self.setup_events_for_2fa_sites()

    def open(self, echo=False):

        self.db_uri = 'postgresql://%(username)s:%(password)s@%(url)s:%(port)s/%(name)s' % self.config.db_config

        self.app.config.update({
            'SQLALCHEMY_DATABASE_URI': self.db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        self.db.init_app(self.app)
        self.db.app = self.app
        BaseModel.set_db(self.db)

        # Init tables
        with self.app.app_context():
            inspector = inspect(self.db.engine)
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
            self.db_in_ram = True
        else:
            self.db_uri = 'sqlite:///%(filename)s' % db_infos

        self.app.config.update({
            'SQLALCHEMY_DATABASE_URI': self.db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo,
            'SQLALCHEMY_ENGINE_OPTIONS': {}
        })

        # Create db engine
        self.db.init_app(self.app)
        self.db.app = self.app
        BaseModel.set_db(self.db)

        with self.app.app_context():
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

    def reset_db(self):
        if not self.db_in_ram:
            return  # Safety: only possible to reset a db if database is in RAM!
        BaseModel.metadata.drop_all(self.db.engine.connect())
        BaseModel.create_all()
        self.create_defaults(self.config, True)

        # Set versions
        from opentera.utils.TeraVersions import TeraVersions
        versions = TeraVersions()
        versions.save_to_db()

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


if __name__ == '__main__':
    with flask_app.app_context():
        config = ConfigManager()
        config.create_defaults()
        manager = DBManager(config)
        print(manager)
        manager.open_local(dict(), echo=True, ram=True)
        manager.create_defaults(config, test=True)
        user_instance = TeraUser()
        user_instance.query.all()
        test = TeraUser.query.all()
        print(test)
