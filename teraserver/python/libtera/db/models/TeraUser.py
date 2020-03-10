from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject

from passlib.hash import bcrypt
import uuid
import datetime
import json


class TeraUser(db.Model, BaseModel):
    __tablename__ = 't_users'
    id_user = db.Column(db.Integer, db.Sequence('id_user_sequence'), primary_key=True, autoincrement=True)
    user_username = db.Column(db.String(50), nullable=False, unique=True)
    user_uuid = db.Column(db.String(36), nullable=False, unique=True)
    user_email = db.Column(db.String, nullable=True)
    user_firstname = db.Column(db.String, nullable=False)
    user_lastname = db.Column(db.String, nullable=False)
    user_password = db.Column(db.String, nullable=False)
    user_enabled = db.Column(db.Boolean, nullable=False)
    user_profile = db.Column(db.String, nullable=False)
    user_notes = db.Column(db.String, nullable=True)
    user_lastonline = db.Column(db.TIMESTAMP, nullable=True)
    user_superadmin = db.Column(db.Boolean, nullable=False)

    user_sites_access = db.relationship('TeraSiteAccess', cascade="all,delete")
    user_projects_access = db.relationship("TeraProjectAccess", cascade="all,delete")

    authenticated = False

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['authenticated', 'user_password', 'user_sites_access', 'user_projects_access'])
        if minimal:
            ignore_fields.extend(['user_username', 'user_email', 'user_profile', 'user_notes', 'user_lastonline',
                                  'user_superadmin'])
        rval = super().to_json(ignore_fields=ignore_fields)
        rval['user_name'] = self.get_fullname()
        return rval

    def get_token(self, token_key: str):
        return TeraUser.get_token_for_user(self.user_uuid, token_key)

    @staticmethod
    def get_token_for_user(user_uuid: uuid, token_key: str):
        import time
        import jwt
        # Creating token with user info
        payload = {
            'iat': int(time.time()),
            'user_uuid': user_uuid
        }

        return jwt.encode(payload, token_key, algorithm='HS256').decode('utf-8')

    def get_fullname(self):
        return self.user_firstname + ' ' + self.user_lastname

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def is_active(self):
        return self.user_enabled

    def get_id(self):
        return self.user_uuid

    def update_last_online(self):
        self.user_lastonline = datetime.datetime.now()
        db.session.commit()

    def __str__(self):
        return '<TeraUser ' + str(self.user_username) + ', ' + str(self.user_email) + ' >'

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def encrypt_password(password):
        return bcrypt.hash(password)

    # @staticmethod
    # def is_anonymous():
    #     return False

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
        user = TeraUser.query.filter_by(user_uuid=u_uuid).first()
        return user

    @staticmethod
    def get_user_by_id(id_user):
        user = TeraUser.query.filter_by(id_user=id_user).first()
        return user

    @classmethod
    def update(cls, id_user: int, values: dict):
        # Remove the password field is present and if empty
        if 'user_password' in values:
            if values['user_password'] == '':
                del values['user_password']
            else:
                values['user_password'] = TeraUser.encrypt_password(values['user_password'])

        # Dumps the user profile if present
        if 'user_profile' in values:
            if isinstance(values['user_profile'], dict):
                values['user_profile'] = json.dumps(values['user_profile'])

        super().update(id_user, values)

    @classmethod
    def insert(cls, user):
        # Encrypts password
        user.user_password = TeraUser.encrypt_password(user.user_password)

        # Generate UUID
        user.user_uuid = str(uuid.uuid4())

        # Clear last online field
        user.user_lastonline = None

        # Converts profile from dict, if needed
        if isinstance(user.user_profile, dict):
            user.user_profile = json.dumps(user.user_profile)

        super().insert(user)

    @staticmethod
    def create_defaults():

        # Admin
        admin = TeraUser()
        admin.user_enabled = True
        admin.user_firstname = "Super"
        admin.user_lastname = "Admin"
        admin.user_profile = ""
        admin.user_password = TeraUser.encrypt_password("admin")
        admin.user_superadmin = True
        admin.user_username = "admin"
        admin.user_uuid = str(uuid.uuid4())
        # admin.user_usergroups.append(TeraUserGroup.get_usergroup_by_name('Administrateurs'))
        db.session.add(admin)

        # Site admin
        admin = TeraUser()
        admin.user_enabled = True
        admin.user_firstname = "Site"
        admin.user_lastname = "Admin"
        admin.user_profile = ""
        admin.user_password = TeraUser.encrypt_password("siteadmin")
        admin.user_superadmin = False
        admin.user_username = "siteadmin"
        admin.user_uuid = str(uuid.uuid4())
        db.session.add(admin)

        # Site User
        user = TeraUser()
        user.user_enabled = True
        user.user_firstname = "Site"
        user.user_lastname = "User"
        user.user_profile = ""
        user.user_password = TeraUser.encrypt_password("user")
        user.user_superadmin = False
        user.user_username = "user"
        user.user_uuid = str(uuid.uuid4())
        db.session.add(user)

        # Site User
        user = TeraUser()
        user.user_enabled = True
        user.user_firstname = "MultiSite"
        user.user_lastname = "User"
        user.user_profile = ""
        user.user_password = TeraUser.encrypt_password("user2")
        user.user_superadmin = False
        user.user_username = "user2"
        user.user_uuid = str(uuid.uuid4())
        db.session.add(user)

        # Project Access
        # admin_access = TeraProjectAccess()
        # admin_access.id_user = TeraUser.get_user_by_username('siteadmin').id_user
        # admin_access.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        # admin_access.project_access_role = 'admin'
        # db.session.add(admin_access)

        user_access = TeraProjectAccess()
        user_access.id_user = TeraUser.get_user_by_username('user').id_user
        user_access.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        user_access.project_access_role = 'user'
        db.session.add(user_access)

        user2_access = TeraProjectAccess()
        user2_access.id_user = TeraUser.get_user_by_username('user2').id_user
        user2_access.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        user2_access.project_access_role = 'user'
        db.session.add(user2_access)

        user2_access_admin = TeraProjectAccess()
        user2_access_admin.id_user = TeraUser.get_user_by_username('user2').id_user
        user2_access_admin.id_project = TeraProject.get_project_by_projectname('Default Project #2').id_project
        user2_access_admin.project_access_role = 'admin'
        db.session.add(user2_access_admin)

        # Site Access
        admin_access = TeraSiteAccess()
        admin_access.id_user = TeraUser.get_user_by_username('siteadmin').id_user
        admin_access.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        admin_access.site_access_role = 'admin'
        db.session.add(admin_access)

        user_access = TeraSiteAccess()
        user_access.id_user = TeraUser.get_user_by_username('user').id_user
        user_access.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        user_access.site_access_role = 'user'
        db.session.add(user_access)

        user2_access = TeraSiteAccess()
        user2_access.id_user = TeraUser.get_user_by_username('user2').id_user
        user2_access.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        user2_access.site_access_role = 'user'
        db.session.add(user2_access)

        db.session.commit()
