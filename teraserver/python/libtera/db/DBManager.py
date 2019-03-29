from libtera.db.Base import db

# Must include all Database objects here to be properly initialized and created if needed


# All at once to make sure all files ar registered.
from libtera.db.models import *

from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.models.TeraSiteAccess import TeraSiteAccess

from modules.FlaskModule.FlaskModule import flask_app


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
        pass

    @staticmethod
    def create_defaults():
        if TeraSite.get_count() == 0:
            print('No sites - creating defaults')
            TeraSite.create_defaults()

        if TeraProject.get_count() == 0:
            print("No projects - creating defaults")
            TeraProject.create_defaults()

        if TeraParticipantGroup.get_count() == 0:
            print("No participant groups - creating defaults")
            TeraParticipantGroup.create_defaults()

        if TeraUser.get_count() == 0:
            print('No users - creating defaults')
            TeraUser.create_defaults()

    @staticmethod
    def open(db_infos, echo=False):
        db_uri = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % db_infos

        flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        db.init_app(flask_app)
        db.app = flask_app

        # Init tables
        db.drop_all()
        db.create_all()

    @staticmethod
    def open_local(db_infos, echo=False):
        db_uri = 'sqlite:///%(filename)s' % db_infos

        flask_app.config.update({
            'SQLALCHEMY_DATABASE_URI': db_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': echo
        })

        # Create db engine
        db.init_app(flask_app)
        db.app = flask_app

        # Init tables
        db.create_all()

    @staticmethod
    def get_user_sites(user: TeraUser, **kwargs):
        if user.user_superadmin:
            return TeraSite.query.filter_by(**kwargs).all()
        else:
            # Only super user can create sites, by default we can list our sites only
            return TeraSite.query.filter(TeraSite.id_site.in_(user.get_accessible_sites_ids())).filter_by(**kwargs).all()

    @staticmethod
    def get_user_projects(user: TeraUser, **kwargs):
        if user.user_superadmin:
            return TeraProject.query.filter_by(**kwargs).all()
        else:
            return TeraProject.query.filter(TeraProject.id_project.in_
                                            (user.get_accessible_projects_ids())).filter_by(**kwargs).all()
