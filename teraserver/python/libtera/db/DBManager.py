from libtera.db.Base import db
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSiteGroup import TeraSiteGroup
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.models.TeraProjectGroup import TeraProjectGroup

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

        if TeraSiteGroup.get_count() == 0:
            print("No sitegroups - creating defaults")
            TeraSiteGroup.create_defaults()

        if TeraProject.get_count() == 0:
            print("No projects - creating defaults")
            TeraProject.create_defaults()

        if TeraProjectGroup.get_count() == 0:
            print("No project groups - creating defaults")
            TeraProjectGroup.create_defaults()

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
            return TeraSite.query.filter(TeraSite.id_site.in_(user.get_accessible_sites())).filter_by(**kwargs).all()

    @staticmethod
    def get_user_projects(user: TeraUser, **kwargs):
        if user.user_superadmin:
            return TeraProject.query.filter_by(**kwargs).all()
        else:
            return TeraProject.query.filter(TeraProject.id_project.in_
                                            (user.get_accessible_projects(read_access=True))).filter_by(**kwargs).all()
