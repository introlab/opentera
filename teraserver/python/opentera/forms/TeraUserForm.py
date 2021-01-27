from opentera.forms.TeraForm import *
from flask_babel import gettext
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class TeraUserForm:

    @staticmethod
    def get_user_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("user")

        # Sections
        section = TeraFormSection("informations", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_user", gettext("User ID"), "hidden", True))
        section.add_item(TeraFormItem("user_uuid", gettext("User UUID"), "hidden"))
        section.add_item(TeraFormItem("user_name", gettext("User Full Name"), "hidden"))
        section.add_item(TeraFormItem("user_username", gettext("Username"), "text", True))
        section.add_item(TeraFormItem("user_enabled", gettext("User Enabled"), "boolean", True, item_default=True))
        section.add_item(TeraFormItem("user_firstname", gettext("First Name"), "text", True))
        section.add_item(TeraFormItem("user_lastname", gettext("Last Name"), "text", True))
        section.add_item(TeraFormItem("user_email", gettext("Email"), "text"))
        section.add_item(
            TeraFormItem("user_password", gettext("Password"), "password", item_options={"confirm": True}))
        section.add_item(TeraFormItem("user_superadmin", gettext("User Is Super Administrator"), "boolean", True))
        section.add_item(TeraFormItem("user_notes", gettext("Notes"), "longtext"))
        section.add_item(TeraFormItem("user_profile", gettext("Profile"), "hidden"))
        section.add_item(TeraFormItem("user_lastonline", gettext("Last Connection"), "datetime",
                                      item_options={"readonly": True}))

        return form.to_dict()

    # @staticmethod
    # def get_user_profile_form():
    #     form = TeraForm("profile")
    #
    #     # Sections
    #     section = TeraFormSection("main_prefs", gettext("Preferences"))
    #     form.add_section(section)
    #
    #     section.add_item(TeraFormItem("language", gettext("Language"), "array", False,
    #                                   [TeraFormValue("fr", gettext("Français")),
    #                                    TeraFormValue("en", gettext("English"))]))
    #     section.add_item(TeraFormItem("notify_sounds", gettext("Activate Notification Sounds"), "boolean", False))

        # section1 = TeraFormSection("main_audio_video", gettext("Configuration audio-vidéo"))
        # form.add_section(section1)
        #
        # # Items
        # section1.add_item(TeraFormItem("camera", gettext("Caméra"), "videoinputs", True))
        # item = TeraFormItem("teracam_type", gettext("Type de caméra"), "array", True,
        #                     [TeraFormValue("0", gettext("Caméra réseau")),
        #                      TeraFormValue("1", gettext("Capture d'écran"))],
        #                     "0", TeraFormItemCondition("camera", "=", "TeraCam"))
        # section1.add_item(item)
        #
        # item = TeraFormItem("teracam_src", gettext("Adresse du flux de la caméra"), "text", True,
        #                     item_condition=TeraFormItemCondition("teracam_type", "=", 0))
        # section1.add_item(item)
        #
        # item = TeraFormItem("teracam_screen_fps", gettext("Trames par seconde"), "array", True,
        #                     ["Maximum", "5", "10", "15",
        #                      "20", "24", "30"],
        #                     item_condition=TeraFormItemCondition("teracam_type", "=", 1))
        # section1.add_item(item)
        # item = TeraFormItem("teracam_screen_res", gettext("Résolution"), "array", True,
        #                     ["Maximum", "160x120", "320x240",
        #                      "640x480", "720x480", "800x600",
        #                      "1024x768", "1280x720", "1440x900",
        #                      "1680x1050", "1920x1080"],
        #                     item_condition=TeraFormItemCondition("teracam_type", "=", 1))
        # section1.add_item(item)
        #
        # section1.add_item(TeraFormItem("camera_ptz", gettext("Caméra contrôlable (PTZ)"), "boolean"))
        # item = TeraFormItem("camera_ptz_type", gettext("Type de contrôle"), "array", True,
        #                   [TeraFormValue("0", gettext("Vivotek")), TeraFormValue("1", gettext("ONVIF (générique)"))],
        #                     item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        # section1.add_item(item)
        # item = TeraFormItem("camera_ptz_ip", gettext("Adresse réseau"), "text", True,
        #                     item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        # section1.add_item(item)
        # item = TeraFormItem("camera_ptz_port", gettext("Port"), "numeric", True,
        #                     item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        # section1.add_item(item)
        # item = TeraFormItem("camera_ptz_username", gettext("Nom utilisateur"), "text", True,
        #                     item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        # section1.add_item(item)
        # item = TeraFormItem("camera_ptz_password", gettext("Mot de passe"), "password", True,
        #                     item_condition=TeraFormItemCondition("camera_ptz", "=", True))
        # section1.add_item(item)
        #
        # section1.add_item(TeraFormItem("audio", gettext("Microphone"), "audioinputs", True))
        # section1.add_item(TeraFormItem("camera2", gettext("Caméra secondaire"), "videoinputs"))
        #
        # section2 = TeraFormSection("options", gettext("Configuration générale"))
        # form.add_section(section2)
        # section2.add_item(TeraFormItem("options_fullscreen", gettext("Affichage en plein écran en séance"), "boolean",
        #                                item_default=True))
        # section2.add_item(TeraFormItem("option_webaccess", gettext("Permettre l'accès via le web"), "boolean",
        #                                item_default=False))

        return form.to_dict()

