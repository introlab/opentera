from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraUserGroup import users_usergroups_table, TeraUserGroup
from sqlalchemy.dialects.postgresql import UUID

from passlib.hash import bcrypt
from enum import Enum
import uuid


class TeraUserTypes(Enum):
    USER = 1
    KIT = 2
    ROBOT = 3


class TeraUser(db.Model, BaseModel):
    __tablename__ = 't_users'
    id_user = db.Column(db.Integer, db.Sequence('id_user_sequence'), primary_key=True, autoincrement=True)
    user_username = db.Column(db.String(50), nullable=False, unique=True)
    user_uuid = db.Column(UUID, nullable=False, unique=True)
    user_email = db.Column(db.String, nullable=True)
    user_firstname = db.Column(db.String, nullable=False)
    user_lastname = db.Column(db.String, nullable=False)
    user_password = db.Column(db.String, nullable=False)
    user_enabled = db.Column(db.Boolean, nullable=False)
    user_type = db.Column(db.SmallInteger, nullable=False)
    user_profile = db.Column(db.String, nullable=False)
    user_notes = db.Column(db.String, nullable=True)
    user_lastonline = db.Column(db.TIMESTAMP, nullable=True)
    user_superadmin = db.Column(db.Boolean, nullable=False)

    user_usergroups = db.relationship("TeraUserGroup", secondary=users_usergroups_table,
                                      back_populates="usergroup_users", cascade="all,delete")

    authenticated = False

    def to_json(self, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['authenticated', 'user_password'])
        rval = super().to_json(ignore_fields=ignore_fields)

        # Add usergroups in json format, if needed
        if 'user_usergroups' in rval:
            usergroups_list = []
            for usergroup in self.user_usergroups:
                usergroups_list.append(usergroup.to_json(ignore_fields=['usergroup_users', 'usergroup_access']))
            rval['user_usergroups'] = usergroups_list

        return rval

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.user_enabled

    def get_id(self):
        return self.user_uuid

    def __str__(self):
        return '<TeraUser ' + str(self.user_username) + ', ' + str(self.user_email) + ' >'

    @staticmethod
    def is_anonymous():
        return False

    @staticmethod
    def get_count():
        user_count = db.session.query(db.func.count(TeraUser.id_user))
        return user_count.first()[0]

    @staticmethod
    def create_default_account():
        user = TeraUser()
        user.user_enabled = True
        user.user_firstname = "Administrateur"
        user.user_lastname = "Systeme"
        user.user_profile = ""
        user.user_password = bcrypt.encrypt("admin")
        user.user_superadmin = True
        user.user_type = TeraUserTypes.USER.value
        user.user_username = "admin"
        user.user_uuid = str(uuid.uuid4())
        user.user_usergroups.append(TeraUserGroup.get_usergroup_by_name('Administrateurs'))
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def verify_password(username, password):
        # Query User with that username
        user = TeraUser.get_user_by_username(username)
        if user is None:
            print('TeraUser: verify_password - user ' + username + ' not found.')
            return None

        # Check if enabled
        if not user.user_enabled:
            print('TeraUser: verify_password - user ' + username + ' is disabled.')
            return None

        # Check password
        if bcrypt.verify(password, user.user_password):
            user.authenticated = True
            return user

        return None

    @staticmethod
    def get_user_by_username(username):
        return TeraUser.query.filter_by(user_username=username).first()

    @staticmethod
    def get_user_by_uuid(u_uuid):
        return TeraUser.query.filter_by(user_uuid=u_uuid).first()

    @staticmethod
    def query_data(filter_args):
        if isinstance(filter_args, tuple):
            return TeraUser.query.filter_by(*filter_args).all()
        if isinstance(filter_args, dict):
            return TeraUser.query.filter_by(**filter_args).all()
        return None

