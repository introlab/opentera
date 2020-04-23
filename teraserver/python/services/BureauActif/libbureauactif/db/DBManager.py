# Using same base as TeraServer
from services.BureauActif.libbureauactif.db.Base import db

# Must include all Database objects here to be properly initialized and created if needed
# All at once to make sure all files are registered.
from services.BureauActif.libbureauactif.db.models import *

from .models.BureauActifData import BureauActifData
from .models.BureauActifTimelineDay import BureauActifTimelineDay
from .models.BureauActifTimelineDayEntry import BureauActifTimelineDayEntry
from .models.BureauActifTimelineEntryType import BureauActifTimelineEntryType
from .models.BureauActifCalendarDay import BureauActifCalendarDay
from .models.BureauActifCalendarData import BureauActifCalendarData
from .models.BureauActifCalendarDataType import BureauActifCalendarDataType

from services.BureauActif.ConfigManager import ConfigManager

from services.BureauActif.FlaskModule import flask_app

from .DBManagerBureauActifCalendarAccess import DBManagerBureauActifCalendarAccess
from .DBManagerBureauActifTimelineAccess import DBManagerBureauActifTimelineAccess

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
    def calendarAccess():
        access = DBManagerBureauActifCalendarAccess()
        return access

    @staticmethod
    def timelineAccess():
        access = DBManagerBureauActifTimelineAccess()
        return access

    def create_defaults(self, config: ConfigManager):
        BureauActifData.create_defaults()
        BureauActifCalendarDataType.create_defaults()
        BureauActifCalendarDay.create_defaults()
        BureauActifCalendarData.create_defaults()
        BureauActifTimelineEntryType.create_defaults()
        BureauActifTimelineDay.create_defaults()
        BureauActifTimelineDayEntry.create_defaults()

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
        db.drop_all()
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

    def upgrade_db(self):
        # TODO ALEMBIC UPGRADES...
        pass

    def stamp_db(self):
        # TODO ALEMBIC UPGRADES
        pass
