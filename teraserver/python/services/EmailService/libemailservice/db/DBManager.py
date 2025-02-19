# Using same base as TeraServer
from opentera.db.Base import BaseModel
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector
from sqlite3 import Connection as SQLite3Connection

# Must include all Database objects here to be properly initialized and created if needed
# All at once to make sure all files are registered.
from services.EmailService.libemailservice.db.models.EmailTemplate import EmailTemplate

from services.EmailService.ConfigManager import ConfigManager
from services.EmailService.FlaskModule import flask_app

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

    def __init__(self, app=flask_app, test: bool = False):
        self.db_uri = None
        self.db = SQLAlchemy()
        self.app = app
        self.test = test

    def create_defaults(self, config: ConfigManager, test: bool = False):
        with self.app.app_context():
            if test:
                # Create test default values
                template = EmailTemplate()
                template.email_template_key = 'GENERAL_TEST_EMAIL'
                template.email_template = 'This is a GLOBAL general test email, using $variable .'
                EmailTemplate.db().session.add(template)

                template = EmailTemplate()
                template.email_template_key = 'PROJECT_EMAIL'
                template.email_template = 'This is a PROJECT test email, using $variable .'
                template.id_project = 1
                EmailTemplate.db().session.add(template)

                template = EmailTemplate()
                template.email_template_key = 'SITE_EMAIL'
                template.email_template = 'This is a SITE test email, using $variable .'
                template.id_site = 2
                EmailTemplate.db().session.add(template)

                template = EmailTemplate()
                template.email_template_key = 'GENERAL_TEST_EMAIL'
                template.email_template = 'This is a PROJECT test email overriding GLOBAL, using $variable .'
                template.id_project = 1
                EmailTemplate.db().session.add(template)

                EmailTemplate.db().session.commit()
            else:
                if EmailTemplate.get_count() == 0:
                    # Create basic templates
                    template = EmailTemplate()
                    template.email_template_key = 'INVITE_EMAIL'
                    template.email_template = ('Hello,<br><br>'
                                               'You\'ve been invited to join sessions on the OpenTera platform.<br><br>'
                                               'To connect to sessions, please click on this link: $join_link.<br><br>'
                                               'You can also add this link to your browser\'s bookmarks.<br><br>'
                                               'Enjoy your sessions!<br><br>$fullname')
                    EmailTemplate.db().session.add(template)

                    template = EmailTemplate()
                    template.email_template_key = 'INVITE_EMAIL'
                    template.email_template_language = 'fr'
                    template.email_template = ('Bonjour,<br><br>'
                                               'Vous êtes invité à participer à des séances via la plateforme OpenTera.<br><br>'
                                               'Pour rejoindre vos séances, veuillez cliquer sur ce lien: $join_link.<br><br>'
                                               'Vous pouvez également ajouter ce lien dans les favoris de votre '
                                               'navigateur<br><br>Bonnes séances!<br><br>$fullname')
                    EmailTemplate.db().session.add(template)

                    EmailTemplate.db().session.commit()


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

# Fix foreign_keys on sqlite
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
