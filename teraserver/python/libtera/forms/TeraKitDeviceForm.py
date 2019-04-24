from libtera.forms.TeraForm import *
from flask_babel import gettext

from libtera.db.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class TeraKitDeviceForm:

    @staticmethod
    def get_kit_device_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("kit_device")

        # Build lists to use
        kits = user_access.get_accessible_kits()
        kits_list = []
        for kit in kits:
            kits_list.append(TeraFormValue(value_id=kit.id_kit, value=kit.kit_name))

        devices = user_access.get_accessible_devices()
        devices_list = []
        for device in devices:
            devices_list.append(TeraFormValue(value_id=device.id_device, value=device.device_name))

        # Sections
        section = TeraFormSection("informations", gettext("Informations"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_kit_device", gettext("ID Lien Kit-Appareil"), "hidden", True))
        section.add_item(TeraFormItem("id_kit", gettext("Kit"), "array", True, item_values=kits_list))
        section.add_item(TeraFormItem("id_device", gettext("Appareil"), "array", True, item_values=devices_list))
        section.add_item(TeraFormItem("kit_device_optional", gettext("Optionnel?"), "boolean", True))

        return form.to_dict()
