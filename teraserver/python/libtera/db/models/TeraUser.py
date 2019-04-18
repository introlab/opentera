from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraKit import TeraKit
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup

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
            ignore_fields.extend(['user_username', 'user_email', 'user_profile', 'user_notes', 'user_lastonline', 'user_superadmin'])
        rval = super().to_json(ignore_fields=ignore_fields)
        rval['user_name'] = self.get_fullname()
        return rval

    def get_fullname(self):
        return self.user_firstname + ' ' + self.user_lastname

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.user_enabled

    def get_id(self):
        return self.user_uuid

    def update_last_online(self):
        self.user_lastonline = datetime.datetime.now()
        db.session.commit()

    def query_user_by_uuid(self, u_uuid):
        user = TeraUser.query.filter_by(user_uuid=u_uuid).first()
        if user is not None:
            accessibles = TeraUser.get_accessible_users_ids(self)
            if user.id_user not in accessibles:
                return None
        return user

    def query_user_by_id(self, id_user):
        user = TeraUser.query.filter_by(id_user=id_user).first()
        if user is not None:
            accessibles = TeraUser.get_accessible_users_ids(self)
            if user.id_user not in accessibles:
                return None

        return user

    def get_accessible_users_ids(self, admin_only=False):
        users = self.get_accessible_users(admin_only=admin_only)
        users_ids = []
        for user in users:
            if user.id_user not in users_ids:
                users_ids.append(user.id_user)
        return users_ids

    def get_accessible_users(self, admin_only=False):
        if self.user_superadmin:
            users = TeraUser.query.all()
        else:
            projects = self.get_accessible_projects(admin_only=admin_only)
            users = []
            for project in projects:
                project_users = project.get_users_in_project()
                for user in project_users:
                    if user not in users:
                        users.append(user)
            # You are always available to yourself!
            if self not in users:
                users.append(self)

        # TODO Sort by username
        return users

    def get_project_role(self, project: TeraProject):
        if self.user_superadmin:
            # SuperAdmin is always admin.
            return 'admin'

        role = TeraProjectAccess.query.filter_by(id_user=self.id_user, id_project=project.id_project).first()

        if role is not None:
            role_name = role.project_access_role
        else:
            # Site admins are always project admins
            site_role = self.get_site_role(project.project_site)
            if site_role == 'admin':
                role_name = 'admin'

        return role_name

    def get_accessible_projects(self, admin_only=False):
        project_list = []
        if self.user_superadmin:
            # Is superadmin - admin on all projects
            project_list = TeraProject.query.all()
        else:
            # Build project list - get sites where user is admin
            for site in self.get_accessible_sites():
                if self.get_site_role(site) == 'admin':
                    project_query = TeraProject.query.filter_by(id_site=site.id_site)
                    if project_query:
                        for project in project_query.all():
                            project_list.append(project)

            # Add specific projects
            for project_access in self.user_projects_access:
                project = project_access.project_access_project
                if project not in project_list:
                    if not admin_only or (admin_only and self.get_project_role(project)=='admin'):
                        project_list.append(project)
        return project_list

    def get_accessible_devices(self, admin_only=False):
        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        return TeraDevice.query.filter(TeraDevice.id_project.in_(project_id_list)).all()

    def get_accessible_kits(self, admin_only=False):
        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        return TeraKit.query.filter(TeraKit.id_project.in_(project_id_list)).all()

    def get_accessible_participants(self, admin_only=False):
        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        groups = TeraParticipantGroup.query.filter(TeraParticipantGroup.id_project.in_(project_id_list)).all()
        participant_list = []
        for group in groups:
            participant_list.extend(TeraParticipant.query.
                                    filter_by(id_participant_group=group.id_participant_group).all())

        return participant_list

    def get_accessible_projects_ids(self, admin_only=False):
        projects = []

        for project in self.get_accessible_projects(admin_only=admin_only):
            projects.append(project.id_project)

        return projects

    def get_projects_roles(self):
        projects_roles = {}
        project_list = self.get_accessible_projects()

        for project in project_list:
            role = self.get_project_role(project)
            projects_roles[project.project_name] = role
        return projects_roles

    def get_accessible_sites(self, admin_only=False):
        if self.user_superadmin:
            site_list = TeraSite.query.all()
        else:
            site_list = []
            for site_access in self.user_sites_access:
                if not admin_only or (admin_only and site_access.site_access_role == 'admin'):
                    site_list.append(site_access.site_access_site)

        return site_list

    def get_accessible_sites_ids(self, admin_only=False):
        sites_ids = []

        for site in self.get_accessible_sites(admin_only=admin_only):
            sites_ids.append(site.id_site)

        return sites_ids

    def get_sites_roles(self):
        sites_roles = {}

        for site in self.get_accessible_sites():
            sites_roles[site] = self.get_site_role(site)

        return sites_roles

    def get_site_role(self, site: TeraSite):
        if self.user_superadmin:
            # SuperAdmin is always admin.
            return 'admin'

        role = TeraSiteAccess.query.filter_by(id_user=self.id_user, id_site=site.id_site).first()
        if role is not None:
            role_name = role.site_access_role
        else:
            role_name = None
        return role_name

    def __str__(self):
        return '<TeraUser ' + str(self.user_username) + ', ' + str(self.user_email) + ' >'

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def encrypt_password(password):
        return bcrypt.hash(password)

    @staticmethod
    def is_anonymous():
        return False

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
    def get_count():
        user_count = db.session.query(db.func.count(TeraUser.id_user))
        return user_count.first()[0]

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

    @staticmethod
    def update_user(id_user, values={}):
        # Remove the password field is present and if empty
        if 'user_password' in values:
            if values['user_password'] == '':
                values.pop('user_password')
            else:
                values['user_password'] = TeraUser.encrypt_password(values['user_password'])

        # Dumps the user profile if present
        if 'user_profile' in values:
            if isinstance(values['user_profile'], dict):
                values['user_profile'] = json.dumps(values['user_profile'])

        TeraUser.query.filter_by(id_user=id_user).update(values)
        db.session.commit()

    @staticmethod
    def insert_user(user):
        user.id_user = None

        # Encrypts password
        user.user_password = TeraUser.encrypt_password(user.user_password)

        # Generate UUID
        user.user_uuid = str(uuid.uuid4())

        # Clear last online field
        user.user_lastonline = None

        # Converts profile from dict, if needed
        if isinstance(user.user_profile, dict):
            user.user_profile = json.dumps(user.user_profile)
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def delete_user(id_user):
        TeraUser.query.filter_by(id_user=id_user).delete()
        db.session.commit()

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
        admin_access = TeraProjectAccess()
        admin_access.id_user = TeraUser.get_user_by_username('siteadmin').id_user
        admin_access.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        admin_access.project_access_role = 'admin'
        db.session.add(admin_access)

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
