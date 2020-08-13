from libtera.forms.TeraForm import *

from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from flask_babel import gettext


class TeraDeviceForm:

    @staticmethod
    def get_device_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("device")

        # Building lists
        #################
        # Device types & subtypes
        device_types = user_access.get_accessible_devices_types()  # TeraDeviceType.get_devices_types()
        device_types_list = []
        for dev_type in device_types:
            name = gettext(dev_type.get_name())
            device_types_list.append(TeraFormValue(value_id=dev_type.id_device_type, value=name))

        # Sections
        section = TeraFormSection("details", gettext("Paramètres"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_device", gettext("ID Appareil"), "hidden", item_required=True))
        section.add_item(TeraFormItem("device_uuid", gettext("UUID Appareil"), "hidden", item_required=True))
        section.add_item(TeraFormItem("device_name", gettext("Nom appareil"), "text", item_required=True))
        section.add_item(TeraFormItem("device_type", gettext("Type appareil"), "array", item_required=True,
                                      item_values=device_types_list))
        section.add_item(TeraFormItem("id_device_subtype", gettext("Sous-type appareil"), "array", item_required=False,
                                      item_condition=TeraFormItemCondition("device_type", "=", "changed",
                                                                           "/api/user/devicesubtypes?id_device_type=")))
        section.add_item(TeraFormItem("device_token", gettext("Jeton d'accès"), "label",
                                      item_options={"readonly": False}))
        section.add_item(TeraFormItem("device_certificate", gettext("Certificat"), "hidden",
                                      item_options={"readonly": True}))
        section.add_item(TeraFormItem("device_enabled", gettext("Activé?"), "boolean", item_required=True))
        section.add_item(TeraFormItem("device_onlineable", gettext("Peut se connecter?"), "boolean",
                                      item_required=True))

        section.add_item(TeraFormItem("device_lastonline", gettext("Dernière connexion"), "label",
                                      item_options={"readonly": True}))

        section3 = TeraFormSection("infos", gettext("Informations"))
        form.add_section(section3)
        section3.add_item(TeraFormItem("device_infos", gettext("Informations"), "longtext"))

        section2 = TeraFormSection("config", gettext("Configuration"))
        form.add_section(section2)
        section2.add_item(TeraFormItem("device_config", gettext("Configuration"), "longtext"))

        section1 = TeraFormSection("notes", gettext("Notes"))
        form.add_section(section1)
        section1.add_item(TeraFormItem("device_notes", gettext("Notes"), "longtext"))

        return form.to_dict()
