from opentera.forms.TeraForm import *

from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from flask_babel import gettext


class TeraServiceConfigForm:

    @staticmethod
    def get_service_config_form():
        form = TeraForm("service_config")

        # Building lists
        #################
        # None to build!

        # Sections
        section = TeraFormSection("infos", gettext("Information"))
        form.add_section(section)

        # service_endpoint = db.Column(db.String, nullable=False)
        # service_clientendpoint = db.Column(db.String, nullable=False)
        # service_enabled = db.Column(db.Boolean, nullable=False, default=False)
        # Items
        section.add_item(TeraFormItem("id_service", gettext("Service ID"), "hidden", item_required=True))
        section.add_item(TeraFormItem("id_service_config", gettext("Service Config ID"), "hidden", item_required=True))
        section.add_item(TeraFormItem("id_user", gettext("User ID"), "hidden", item_required=False))
        section.add_item(TeraFormItem("id_device", gettext("Device ID"), "hidden", item_required=False))
        section.add_item(TeraFormItem("id_participant", gettext("Participant ID"), "hidden", item_required=False))
        section.add_item(TeraFormItem("service_config_config", gettext("Service Config"), "hidden", item_required=True))

        form_dict = form.to_dict()

        # if service.has_config_schema():
        #     import json
        #     config_json = json.loads(service.service_config_schema)
        #     form_dict.update(config_json)

        return form_dict

    @staticmethod
    def get_service_config_config_form(user_access: DBManagerTeraUserAccess, service_key: str):
        form = TeraForm("service_config_config")

        if service_key == 'VideoRehabService':
            # Sections
            section1 = TeraFormSection("main_audio_video", gettext("Multimedia Configuration"))
            form.add_section(section1)

            # Items
            section1.add_item(TeraFormItem("camera", gettext("Camera"), "videoinputs", False))
            section1.add_item(TeraFormItem("mirror", gettext("Mirrored image"), "boolean", False, item_default=True))
            item = TeraFormItem("teracam_type", gettext("Camera Type"), "array", True,
                                [TeraFormValue("0", gettext("Network Camera")),
                                 TeraFormValue("1", gettext("Screen Capture"))],
                                "0", TeraFormItemCondition("camera", "=", "TeraCam"))
            section1.add_item(item)

            item = TeraFormItem("teracam_src", gettext("RTSP URL"), "text", True,
                                item_condition=TeraFormItemCondition("teracam_type", "=", 0))
            section1.add_item(item)

            item = TeraFormItem("teracam_screen_fps", gettext("Frames per second (FPS)"), "array", True,
                                ["Maximum", "5", "10", "15",
                                 "20", "24", "30"],
                                item_condition=TeraFormItemCondition("teracam_type", "=", 1))
            section1.add_item(item)
            item = TeraFormItem("teracam_screen_res", gettext("Resolution"), "array", True,
                                ["Maximum", "160x120", "320x240",
                                 "640x480", "720x480", "800x600",
                                 "1024x768", "1280x720", "1440x900",
                                 "1680x1050", "1920x1080"],
                                item_condition=TeraFormItemCondition("teracam_type", "=", 1))
            section1.add_item(item)

            section1.add_item(TeraFormItem("camera_ptz", gettext("Pan-Tilt-Zoom Camera"), "boolean"))
            item = TeraFormItem("camera_ptz_type", gettext("Control Type"), "array", True,
                                [TeraFormValue("0", gettext("Vivotek")),
                                 TeraFormValue("1", gettext("ONVIF (Generic)"))],
                                item_condition=TeraFormItemCondition("camera_ptz", "=", True))
            section1.add_item(item)
            item = TeraFormItem("camera_ptz_ip", gettext("Network Address"), "text", True,
                                item_condition=TeraFormItemCondition("camera_ptz", "=", True))
            section1.add_item(item)
            item = TeraFormItem("camera_ptz_port", gettext("Port"), "numeric", True,
                                item_condition=TeraFormItemCondition("camera_ptz", "=", True))
            section1.add_item(item)
            item = TeraFormItem("camera_ptz_username", gettext("Username"), "text", True,
                                item_condition=TeraFormItemCondition("camera_ptz", "=", True))
            section1.add_item(item)
            item = TeraFormItem("camera_ptz_password", gettext("Password"), "password", True,
                                item_condition=TeraFormItemCondition("camera_ptz", "=", True))
            section1.add_item(item)

            section1.add_item(TeraFormItem("audio", gettext("Microphone"), "audioinputs", False))
            section1.add_item(TeraFormItem("camera2", gettext("Secondary Camera"), "videoinputs"))

        return form.to_dict()
