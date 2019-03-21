from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraUserGroup import users_usergroups_table, TeraUserGroup
from libtera.db.models.TeraAccess import TeraAccess
from libtera.db.models.TeraForm import TeraForm, TeraFormSection, TeraFormItem, TeraFormItemCondition, TeraFormValue
from sqlalchemy.dialects.postgresql import UUID

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

    def update_last_online(self):
        self.user_lastonline = datetime.datetime.now()
        db.session.commit()

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

        # Admin
        admin = TeraUser()
        admin.user_enabled = True
        admin.user_firstname = "Administrateur"
        admin.user_lastname = "Systeme"
        admin.user_profile = ""
        admin.user_password = bcrypt.hash("admin")
        admin.user_superadmin = True
        admin.user_type = TeraUserTypes.USER.value
        admin.user_username = "admin"
        admin.user_uuid = str(uuid.uuid4())
        admin.user_usergroups.append(TeraUserGroup.get_usergroup_by_name('Administrateurs'))
        db.session.add(admin)

        # User
        user = TeraUser()
        user.user_enabled = True
        user.user_firstname = "User"
        user.user_lastname = "Systeme"
        user.user_profile = ""
        user.user_password = bcrypt.hash("user")
        user.user_superadmin = False
        user.user_type = TeraUserTypes.USER.value
        user.user_username = "user"
        user.user_uuid = str(uuid.uuid4())
        user.user_usergroups.append(TeraUserGroup.get_usergroup_by_name('Users'))
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

