from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from sqlalchemy import Column, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSessionUsers import TeraSessionUsers
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraAsset import TeraAsset


from passlib.hash import bcrypt
import uuid
import datetime
import json


# Generator for jti
def infinite_jti_sequence():
    num = 0
    while True:
        yield num
        num += 1


# Initialize generator, call next(user_jti_generator) to get next sequence number
user_jti_generator = infinite_jti_sequence()


class TeraUser(BaseModel, SoftDeleteMixin):
    __tablename__ = 't_users'
    id_user = Column(Integer, Sequence('id_user_sequence'), primary_key=True, autoincrement=True)
    user_username = Column(String(50), nullable=False, unique=True)
    user_uuid = Column(String(36), nullable=False, unique=True)
    user_email = Column(String, nullable=True)
    user_firstname = Column(String, nullable=False)
    user_lastname = Column(String, nullable=False)
    user_password = Column(String, nullable=False)
    user_enabled = Column(Boolean, nullable=False)
    user_profile = Column(String, nullable=False)  # Used to store "extra" informations, if needed.
    user_notes = Column(String, nullable=True)
    user_lastonline = Column(TIMESTAMP(timezone=True), nullable=True)
    user_superadmin = Column(Boolean, nullable=False, default=False)

    # user_sites_access = relationship('TeraSiteAccess', cascade="all,delete")
    # user_projects_access = relationship("TeraProjectAccess", cascade="all,delete")
    user_user_groups = relationship("TeraUserGroup", secondary="t_users_users_groups",
                                    back_populates="user_group_users", lazy='joined')
    user_sessions = relationship("TeraSession", secondary="t_sessions_users", back_populates="session_users",
                                 passive_deletes=True)

    user_created_sessions = relationship("TeraSession", cascade='delete', back_populates='session_creator_user',
                                         passive_deletes=True)

    user_service_config = relationship("TeraServiceConfig", cascade='delete', passive_deletes=True)

    user_assets = relationship("TeraAsset", cascade='delete', back_populates='asset_user', passive_deletes=True)
    user_tests = relationship("TeraTest", cascade='delete', back_populates='test_user', passive_deletes=True)

    authenticated = False

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['authenticated', 'user_password', 'user_user_groups',
                              'user_sessions'])
        if minimal:
            ignore_fields.extend(['user_username', 'user_email', 'user_profile', 'user_notes', 'user_lastonline',
                                  'user_superadmin'])
        rval = super().to_json(ignore_fields=ignore_fields)
        rval['user_name'] = self.get_fullname()
        return rval

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_user': self.id_user, 'user_uuid': self.user_uuid}

    def get_token(self, token_key: str, expiration=3600):
        import time
        import jwt

        # Creating token with user info
        now = time.time()

        payload = {
            'iat': int(now),
            'exp': int(now) + expiration,
            'iss': 'TeraServer',
            'jti': next(user_jti_generator),
            'user_uuid': self.user_uuid,
            'id_user': self.id_user,
            'user_fullname': self.get_fullname(),
            'user_superadmin': self.user_superadmin
        }

        return jwt.encode(payload, token_key, algorithm='HS256')

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
        TeraUser.db().session.commit()

    def __str__(self):
        return '<TeraUser ' + str(self.user_username) + ', ' + str(self.user_email) + ' >'

    def __repr__(self):
        return self.__str__()

    def get_sites_roles(self) -> dict:
        sites_roles = {}

        if self.user_superadmin:
            # Super admin - admin role in all sites
            sites = TeraSite.query.all()
            for site in sites:
                sites_roles[site] = {'site_role': 'admin', 'inherited': True}
            return sites_roles

        # Browse all user groups to get roles for those sites
        for user_group in self.user_user_groups:
            user_group_roles = user_group.get_sites_roles()
            for site, site_role in user_group_roles.items():
                if site not in sites_roles:
                    # Site not already present
                    sites_roles[site] = site_role
                else:
                    # Site present - check if we have an "admin" role to overwrite an "user" role
                    if site_role['site_role'] == 'admin':
                        sites_roles[site] = site_role

        return sites_roles

    def get_projects_roles(self) -> dict:
        projects_roles = {}

        if self.user_superadmin:
            # Super admin - admin role in all projects
            projects = TeraProject.query.all()
            for project in projects:
                projects_roles[project] = {'project_role': 'admin', 'inherited': True}
            return projects_roles

        # Browse all user groups to get roles for those projects
        for user_group in self.user_user_groups:
            user_group_roles = user_group.get_projects_roles()
            for project, project_role in user_group_roles.items():
                if project not in projects_roles:
                    # Project not already present
                    projects_roles[project] = project_role
                else:
                    # Project present - check if we have an "admin" role to overwrite an "user" role
                    if project_role['project_role'] == 'admin':
                        projects_roles[project] = project_role

        return projects_roles

    @staticmethod
    def encrypt_password(password):
        return bcrypt.hash(password)

    @staticmethod
    def verify_password(username, password, user=None):
        # Query User with that username
        if user is None:
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
    def get_user_by_username(username, with_deleted: bool = False):
        return TeraUser.query.execution_options(include_deleted=with_deleted).filter_by(user_username=username).first()

    @staticmethod
    def get_user_by_uuid(u_uuid, with_deleted: bool = False):
        user = TeraUser.query.execution_options(include_deleted=with_deleted).filter_by(user_uuid=u_uuid).first()
        return user

    @staticmethod
    def get_user_by_id(id_user, with_deleted: bool = False):
        user = TeraUser.query.execution_options(include_deleted=with_deleted).filter_by(id_user=id_user).first()
        return user

    @staticmethod
    def get_superadmins(with_deleted: bool = False):
        return TeraUser.query.execution_options(include_deleted=with_deleted).filter_by(user_superadmin=True).all()

    @classmethod
    def update(cls, id_user: int, values: dict):
        # Remove the password field is present and if empty
        if 'user_password' in values:
            if values['user_password'] == '':
                del values['user_password']
            else:
                # Forcing password to string
                values['user_password'] = TeraUser.encrypt_password(str(values['user_password']))

        # Dumps the user profile if present
        if 'user_profile' in values:
            if isinstance(values['user_profile'], dict):
                values['user_profile'] = json.dumps(values['user_profile'])

        # Prevent changes on UUID
        if 'user_uuid' in values:
            del values['user_uuid']

        super().update(id_user, values)

    @classmethod
    def insert(cls, user):
        # Encrypts password
        # Forcing password to string
        user.user_password = TeraUser.encrypt_password(str(user.user_password))

        # Generate UUID
        user.user_uuid = str(uuid.uuid4())

        # Clear last online field
        user.user_lastonline = None

        # Converts profile from dict, if needed
        if isinstance(user.user_profile, dict):
            user.user_profile = json.dumps(user.user_profile)

        super().insert(user)

    def delete_check_integrity(self) -> IntegrityError | None:
        if TeraSessionUsers.get_session_count_for_user(self.id_user) > 0:
            return IntegrityError('User still has sessions', self.id_user, 't_sessions_users')

        if TeraSession.get_count(filters={'id_creator_user': self.id_user}) > 0:
            return IntegrityError('User still has created sessions', self.id_user, 't_sessions')

        if TeraAsset.get_count(filters={'id_user': self.id_user}) > 0:
            return IntegrityError('User still has created assets', self.id_user, 't_assets')

        if TeraTest.get_count(filters={'id_user': self.id_user}) > 0:
            return IntegrityError('User still has created tests', self.id_user, 't_tests')

        return None

    @staticmethod
    def create_defaults(test=False):
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
        TeraUser.db().session.add(admin)

        if test:
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
            # admin.user_user_group = TeraUserGroup.get_user_group_by_group_name("Admins - Default Site")
            TeraUser.db().session.add(admin)

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
            # user.user_user_group = TeraUserGroup.get_user_group_by_group_name("Users - Project 1")
            TeraUser.db().session.add(user)

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
            # user.user_user_group = TeraUserGroup.get_user_group_by_group_name("Users - Projects 1 & 2")
            TeraUser.db().session.add(user)

            # Project admin
            user = TeraUser()
            user.user_enabled = True
            user.user_firstname = "Project"
            user.user_lastname = "Admin"
            user.user_profile = ""
            user.user_password = TeraUser.encrypt_password("user3")
            user.user_superadmin = False
            user.user_username = "user3"
            user.user_uuid = str(uuid.uuid4())
            # user.user_user_group = TeraUserGroup.get_user_group_by_group_name("Users - Projects 1 & 2")
            TeraUser.db().session.add(user)

            # No access user!
            user = TeraUser()
            user.user_enabled = True
            user.user_firstname = "No Access"
            user.user_lastname = "User!"
            user.user_profile = ""
            user.user_password = TeraUser.encrypt_password("user4")
            user.user_superadmin = False
            user.user_username = "user4"
            user.user_uuid = str(uuid.uuid4())
            # user.user_user_group = TeraUserGroup.get_user_group_by_group_name("Users - Projects 1 & 2")
            TeraUser.db().session.add(user)

        TeraUser.db().session.commit()
