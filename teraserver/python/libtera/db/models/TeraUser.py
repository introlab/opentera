from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraSiteGroup import users_sitegroups_table, TeraSiteGroup
from libtera.db.models.TeraProjectGroup import users_projectgroups_table, TeraProjectGroup
from libtera.db.models.TeraForm import TeraForm, TeraFormSection, TeraFormItem, TeraFormItemCondition, TeraFormValue

from passlib.hash import bcrypt
from enum import Enum
import uuid
import datetime


class TeraUserTypes(Enum):
    USER = 1
    KIT = 2
    ROBOT = 3


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
    user_type = db.Column(db.SmallInteger, nullable=False)
    user_profile = db.Column(db.String, nullable=False)
    user_notes = db.Column(db.String, nullable=True)
    user_lastonline = db.Column(db.TIMESTAMP, nullable=True)
    user_superadmin = db.Column(db.Boolean, nullable=False)

    user_sitegroups = db.relationship("TeraSiteGroup", secondary=users_sitegroups_table,
                                      back_populates="sitegroup_users", cascade="all,delete")

    user_projectgroups = db.relationship("TeraProjectGroup", secondary=users_projectgroups_table,
                                         back_populates="projectgroup_users", cascade="all,delete")

    authenticated = False

    def to_json(self, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['authenticated', 'user_password'])
        rval = super().to_json(ignore_fields=ignore_fields)

        # Add usergroups in json format, if needed
        if 'user_sitegroups' in rval:
            usersitegroups_list = []
            for usersitegroup in self.user_usergroups:
                usersitegroups_list.append(usersitegroup.to_json(ignore_fields=['sitegroup_users']))
            rval['user_sitegroups'] = usersitegroups_list

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

    def __str__(self):
        return '<TeraUser ' + str(self.user_username) + ', ' + str(self.user_email) + ' >'

    def __repr__(self):
        return self.__str__()

    def get_accessible_sites(self):
        sites = []
        for group in self.user_sitegroups:
            sites.append(group.id_site)

        return sites

    def get_accessible_projects(self, create_access=False, read_access=False, update_access=False, delete_access=False):
        projects = []

        for group in self.user_sitegroups:

            valid = group.has_create_access('projects') & create_access or \
                    group.has_read_access('projects') & read_access or \
                    group.has_update_access('projects') & update_access or \
                    group.has_delete_access('projects') & delete_access

            if valid:
                for project in self.user_projectgroups:
                    projects.append(project.id_project)

        return projects

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
        admin.user_type = TeraUserTypes.USER.value
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
        admin.user_type = TeraUserTypes.USER.value
        admin.user_username = "siteadmin"
        admin.user_uuid = str(uuid.uuid4())
        admin.user_sitegroups.append(TeraSiteGroup.get_sitegroup_by_name('Admin - Default Site'))
        admin.user_projectgroups.append(TeraProjectGroup.get_projectgroup_by_name('Admin - Default Project #1'))
        db.session.add(admin)

        # Site User
        user = TeraUser()
        user.user_enabled = True
        user.user_firstname = "Site"
        user.user_lastname = "User"
        user.user_profile = ""
        user.user_password = bcrypt.hash("user")
        user.user_superadmin = False
        user.user_type = TeraUserTypes.USER.value
        user.user_username = "user"
        user.user_uuid = str(uuid.uuid4())
        user.user_sitegroups.append(TeraSiteGroup.get_sitegroup_by_name('User - Default Site'))
        user.user_projectgroups.append(TeraProjectGroup.get_projectgroup_by_name('User - Default Project #1'))
        db.session.add(user)

        # Site User
        user = TeraUser()
        user.user_enabled = True
        user.user_firstname = "MultiSite"
        user.user_lastname = "User"
        user.user_profile = ""
        user.user_password = bcrypt.hash("user2")
        user.user_superadmin = False
        user.user_type = TeraUserTypes.USER.value
        user.user_username = "user2"
        user.user_uuid = str(uuid.uuid4())
        user.user_sitegroups.append(TeraSiteGroup.get_sitegroup_by_name('User - Default Site'))
        user.user_projectgroups.append(TeraProjectGroup.get_projectgroup_by_name('User - Default Project #1'))
        user.user_projectgroups.append(TeraProjectGroup.get_projectgroup_by_name('User - Default Project #2'))
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

    @staticmethod
    def get_all_user_access(u_uuid):
        access_list = []
        user = TeraUser.query.filter_by(user_uuid=u_uuid).first()
        if user:
            for group in user.user_usergroups:
                access_list.append(group.usergroup_access)

        return access_list

    @staticmethod
    def get_profile_def():
        form = TeraForm("profile")

        # Sections
        section1 = TeraFormSection("main_audio_video", "Configuration audio-vidéo")
        form.add_section(section1)

        # Items
        section1.add_item(TeraFormItem("camera", "Caméra", "videoinputs", True))
        item = TeraFormItem("teracam_type", "Type de caméra", "array", True, [TeraFormValue("0", "Caméra réseau"),
                                                                              TeraFormValue("1", "Capture d'écran")],
                            "0", TeraFormItemCondition("camera", "=", "TeraCam"))
        section1.add_item(item)

        item = TeraFormItem("teracam_src", "Adresse du flux de la caméra", "text", True,
                            item_condition=TeraFormItemCondition("teracam_type", "=", 0))
        section1.add_item(item)

        item = TeraFormItem("teracam_screen_fps", "Trames par seconde", "array", True, ["Maximum", "5", "10", "15",
                                                                                        "20", "24", "30"],
                            item_condition=TeraFormItemCondition("teracam_type", "=", 1))
        section1.add_item(item)
        item = TeraFormItem("teracam_screen_res", "Résolution", "array", True, ["Maximum", "160x120", "320x240",
                                                                                "640x480", "720x480", "800x600",
                                                                                "1024x768", "1280x720", "1440x900",
                                                                                "1680x1050", "1920x1080"],
                            item_condition=TeraFormItemCondition("teracam_type", "=", 1))
        section1.add_item(item)

        section1.add_item(TeraFormItem("camera_ptz", "Caméra contrôlable (PTZ)", "boolean"))
        item = TeraFormItem("camera_ptz_type", "Type de contrôle", "array", True, [TeraFormValue("0", "Vivotek"),
                                                                                   TeraFormValue("1",
                                                                                                 "ONVIF (générique)")],
                            item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        section1.add_item(item)
        item = TeraFormItem("camera_ptz_ip", "Adresse réseau", "text", True,
                            item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        section1.add_item(item)
        item = TeraFormItem("camera_ptz_port", "Port", "numeric", True,
                            item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        section1.add_item(item)
        item = TeraFormItem("camera_ptz_username", "Nom utilisateur", "text", True,
                            item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        section1.add_item(item)
        item = TeraFormItem("camera_ptz_password", "Mot de passe", "password", True,
                            item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        section1.add_item(item)

        section1.add_item(TeraFormItem("audio", "Microphone", "audioinputs", True))
        section1.add_item(TeraFormItem("camera2", "Caméra secondaire", "videoinputs"))

        section2 = TeraFormSection("options", "Configuration générale")
        form.add_section(section2)
        section2.add_item(TeraFormItem("options_fullscreen", "Affichage en plein écran en séance", "boolean",
                                       item_default=True))
        section2.add_item(TeraFormItem("option_webaccess", "Permettre l'accès via le web", "boolean",
                                       item_default=False))

        return form.to_dict()

    @staticmethod
    def get_user_def():
        form = TeraForm("user")

        # Sections
        section = TeraFormSection("informations", "Informations")
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_user", "ID Utilisateur", "hidden", True))
        section.add_item(TeraFormItem("user_uuid", "UUID Utilisateur", "hidden"))
        section.add_item(TeraFormItem("user_username", "Code utilisateur", "text", True))
        section.add_item(TeraFormItem("user_enabled", "Activé", "boolean", True))
        section.add_item(TeraFormItem("user_firstname", "Prénom", "text", True))
        section.add_item(TeraFormItem("user_lastname", "Nom", "text", True))
        section.add_item(TeraFormItem("user_email", "Courriel", "text"))
        section.add_item(TeraFormItem("user_password", "Mot de passe", "password", item_options={"confirm": True}))
        section.add_item(TeraFormItem("user_usergroups", "Groupe(s) utilisateur(s)", "checklist", True))
        section.add_item(TeraFormItem("user_superadmin", "Super administrateur", "boolean", True))
        section.add_item(TeraFormItem("user_notes", "Notes", "longtext"))
        section.add_item(TeraFormItem("user_lastonline", "Dernière connexion", "label",
                                      item_options={"readonly": True}))

        return form.to_dict()
