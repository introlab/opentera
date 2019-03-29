from libtera.db.Base import db, BaseModel
from libtera.forms.TeraForm import TeraForm, TeraFormSection, TeraFormItem, TeraFormItemCondition, TeraFormValue
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject

from passlib.hash import bcrypt
import uuid
import datetime
from flask_babel import gettext


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

    def to_json(self, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['authenticated', 'user_password', 'user_sites_access', 'user_projects_access'])
        rval = super().to_json(ignore_fields=ignore_fields)

        # Add usergroups in json format, if needed
        # if 'user_sitegroups' in rval:
        #     usersitegroups_list = []
        #     for usersitegroup in self.user_usergroups:
        #         usersitegroups_list.append(usersitegroup.to_json(ignore_fields=['sitegroup_users']))
        #     rval['user_sitegroups'] = usersitegroups_list

        return rval

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
        accessibles = TeraUser.get_accessible_users_ids_for_user(self)
        if user.id_user not in accessibles:
            return None
        return user

    def get_accessible_users_ids(self):
        users = self.get_accessible_users()
        users_ids = []
        for user in users:
            if user.id_user not in users_ids:
                users_ids.append(user.id_user)
        return users_ids

    def get_accessible_users(self):
        projects = self.get_accessible_projects()
        users = []
        for project in projects:
            project_users = project.get_users_in_project()
            for user in project_users:
                if user not in users:
                    users.append(user)

        # If superadmin, also add superadmin users
        if self.user_superadmin:
            superadmins = TeraUser.query.filter(TeraUser.user_superadmin).all()
            for superadmin in superadmins:
                if superadmin not in users:
                    users.append(superadmin)

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
            site_role = TeraSiteAccess.get_site_role_for_user(user, project.project_site)
            if site_role == 'admin':
                role_name = 'admin'

        return role_name

    def get_accessible_projects(self):
        project_list = []
        if self.user_superadmin:
            # Is superadmin - admin on all projects
            project_list = TeraProject.query.all()
        else:
            # Build project list - get sites
            for site in self.get_accessible_sites():
                if self.get_site_role_for_user(site) == 'admin':
                    project_query = TeraProject.query.filter_by(id_site=site.id_site)
                    if project_query:
                        for project in project_query.all():
                            project_list.append(project)

            # Add specific projects
            for project_access in self.user_projects_access:
                project = project_access.project_access_project
                if project not in project_list:
                    project_list.append(project)
        return project_list

    def get_accessible_projects_ids(self):
        projects = []

        for project in self.get_accessible_projects():
            projects.append(project.id_project)

        return projects

    def get_projects_roles(self):
        projects_roles = {}
        project_list = self.get_accessible_projects()

        for project in project_list:
            role = self.get_project_role(project)
            projects_roles[project.project_name] = role
        return projects_roles

    def get_accessible_sites(self):
        if self.user_superadmin:
            site_list = TeraSite.query.all()
        else:
            site_list = []
            for site_access in self.user_sites_access:
                site_list.append(site_access.site_access_site)

        return site_list

    def get_accessible_sites_ids(self):
        sites_ids = []

        for site in self.get_accessible_sites():
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
    def is_anonymous():
        return False

    @staticmethod
    def get_count():
        user_count = db.session.query(db.func.count(TeraUser.id_user))
        return user_count.first()[0]

    @staticmethod
    def create_defaults():

        # Admin
        admin = TeraUser()
        admin.user_enabled = True
        admin.user_firstname = "Super"
        admin.user_lastname = "Admin"
        admin.user_profile = ""
        admin.user_password = bcrypt.hash("admin")
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
        admin.user_password = bcrypt.hash("siteadmin")
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
        user.user_password = bcrypt.hash("user")
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
        user.user_password = bcrypt.hash("user2")
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
    def get_profile_def():
        form = TeraForm("profile")

        # Sections
        section1 = TeraFormSection("main_audio_video", gettext("Configuration audio-vidéo"))
        form.add_section(section1)

        # Items
        section1.add_item(TeraFormItem("camera", gettext("Caméra"), "videoinputs", True))
        item = TeraFormItem("teracam_type", gettext("Type de caméra"), "array", True,
                            [TeraFormValue("0", gettext("Caméra réseau")),
                             TeraFormValue("1", gettext("Capture d'écran"))],
                            "0", TeraFormItemCondition("camera", "=", "TeraCam"))
        section1.add_item(item)

        item = TeraFormItem("teracam_src", gettext("Adresse du flux de la caméra"), "text", True,
                            item_condition=TeraFormItemCondition("teracam_type", "=", 0))
        section1.add_item(item)

        item = TeraFormItem("teracam_screen_fps", gettext("Trames par seconde"), "array", True, ["Maximum", "5", "10", "15",
                                                                                        "20", "24", "30"],
                            item_condition=TeraFormItemCondition("teracam_type", "=", 1))
        section1.add_item(item)
        item = TeraFormItem("teracam_screen_res", gettext("Résolution"), "array", True, ["Maximum", "160x120", "320x240",
                                                                                "640x480", "720x480", "800x600",
                                                                                "1024x768", "1280x720", "1440x900",
                                                                                "1680x1050", "1920x1080"],
                            item_condition=TeraFormItemCondition("teracam_type", "=", 1))
        section1.add_item(item)

        section1.add_item(TeraFormItem("camera_ptz", gettext("Caméra contrôlable (PTZ)"), "boolean"))
        item = TeraFormItem("camera_ptz_type", gettext("Type de contrôle"), "array", True,
                            [TeraFormValue("0", gettext("Vivotek")), TeraFormValue("1", gettext("ONVIF (générique)"))],
                            item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        section1.add_item(item)
        item = TeraFormItem("camera_ptz_ip", gettext("Adresse réseau"), "text", True,
                            item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        section1.add_item(item)
        item = TeraFormItem("camera_ptz_port", gettext("Port"), "numeric", True,
                            item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        section1.add_item(item)
        item = TeraFormItem("camera_ptz_username", gettext("Nom utilisateur"), "text", True,
                            item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        section1.add_item(item)
        item = TeraFormItem("camera_ptz_password", gettext("Mot de passe"), "password", True,
                            item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        section1.add_item(item)

        section1.add_item(TeraFormItem("audio", gettext("Microphone"), "audioinputs", True))
        section1.add_item(TeraFormItem("camera2", gettext("Caméra secondaire"), "videoinputs"))

        section2 = TeraFormSection("options", gettext("Configuration générale"))
        form.add_section(section2)
        section2.add_item(TeraFormItem("options_fullscreen", gettext("Affichage en plein écran en séance"), "boolean",
                                       item_default=True))
        section2.add_item(TeraFormItem("option_webaccess", gettext("Permettre l'accès via le web"), "boolean",
                                       item_default=False))

        return form.to_dict()

    @staticmethod
    def get_user_def():
        form = TeraForm("user")

        # Sections
        section = TeraFormSection("informations", gettext("Informations"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_user", gettext("ID Utilisateur"), "hidden", True))
        section.add_item(TeraFormItem("user_uuid", gettext("UUID Utilisateur"), "hidden"))
        section.add_item(TeraFormItem("user_username", gettext("Code utilisateur"), "text", True))
        section.add_item(TeraFormItem("user_enabled", gettext("Activé"), "boolean", True))
        section.add_item(TeraFormItem("user_firstname", gettext("Prénom"), "text", True))
        section.add_item(TeraFormItem("user_lastname", gettext("Nom"), "text", True))
        section.add_item(TeraFormItem("user_email", gettext("Courriel"), "text"))
        section.add_item(TeraFormItem("user_password", gettext("Mot de passe"), "password", item_options={"confirm": True}))
        section.add_item(TeraFormItem("user_usergroups", gettext("Groupe(s) utilisateur(s)"), "checklist", True))
        section.add_item(TeraFormItem("user_superadmin", gettext("Super administrateur"), "boolean", True))
        section.add_item(TeraFormItem("user_notes", gettext("Notes"), "longtext"))
        section.add_item(TeraFormItem("user_lastonline", gettext("Dernière connexion"), "label",
                                      item_options={"readonly": True}))

        return form.to_dict()
