from libtera.forms.TeraForm import *
from libtera.db.models.TeraDeviceType import TeraDeviceType

from libtera.db.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from flask_babel import gettext


class TeraDeviceForm:

    @staticmethod
    def get_device_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("device")

        # Building lists
        device_types = TeraDeviceType.get_devices_types()
        device_types_list = []
        for dev_type in device_types:
            name = ''
            if dev_type.id_device_type == TeraDeviceType.DeviceTypeEnum.VIDEOCONFERENCE.value:
                name = gettext('Vidéconférence')
            if dev_type.id_device_type == TeraDeviceType.DeviceTypeEnum.SENSOR.value:
                name = gettext('Capteur')
            if dev_type.id_device_type == TeraDeviceType.DeviceTypeEnum.ROBOT.value:
                name = gettext('Robot')
            device_types_list.append(TeraFormValue(value_id=dev_type.id_device_type, value=name))

        # Sections
        section = TeraFormSection("informations", gettext("Informations"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_device", gettext("ID Appareil"), "hidden", item_required=True))
        section.add_item(TeraFormItem("device_uuid", gettext("UUID Appareil"), "hidden", item_required=True))
        section.add_item(TeraFormItem("device_name", gettext("Nom appareil"), "text", item_required=True))
        section.add_item(TeraFormItem("device_type", gettext("Type appareil"), "array", item_required=True,
                                      item_values=device_types_list))
        section.add_item(TeraFormItem("device_token", gettext("Jeton d'accès"), "longtext",
                                      item_options={"readonly": True}))
        section.add_item(TeraFormItem("device_certificate", gettext("Certificat"), "hidden",
                                      item_options={"readonly": True}))
        section.add_item(TeraFormItem("device_enabled", gettext("Activé?"), "boolean", item_required=True))
        section.add_item(TeraFormItem("device_optional", gettext("Optionel?"), "boolean"))
        section.add_item(TeraFormItem("device_onlineable", gettext("Peut se connecter?"), "boolean",
                                      item_required=True))
        section.add_item(TeraFormItem("device_notes", gettext("Notes"), "longtext"))
        section.add_item(TeraFormItem("device_lastonline", gettext("Dernière connexion"), "label",
                                      item_options={"readonly": True}))

        section2 = TeraFormSection("config", gettext("Configuration"))
        form.add_section(section2)
        section2.add_item(TeraFormItem("device_config", gettext("Configuration"), "longtext"))

        return form.to_dict()
