from libtera.forms.TeraForm import *

from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from flask_babel import gettext


class TeraDeviceSubTypeForm:

    @staticmethod
    def get_device_subtype_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("device_subtype")

        # Building lists
        #################
        # Device types
        from libtera.db.models.TeraDeviceType import TeraDeviceType
        device_types = TeraDeviceType.get_devices_types()
        device_types_list = []
        for dev_type in device_types:
            name = gettext(dev_type.get_name())
            device_types_list.append(TeraFormValue(value_id=dev_type.id_device_type, value=name))

        # Sections
        section = TeraFormSection("infos", gettext("Informations"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_device_subtype", gettext("ID Sous-type appareil"), "hidden",
                                      item_required=True))
        section.add_item(TeraFormItem("device_subtype_name", gettext("Nom du sous-type d'appareil"), "text",
                                      item_required=True))
        section.add_item(TeraFormItem("id_device_type", gettext("Type appareil"), "array", item_required=True,
                                      item_values=device_types_list))

        return form.to_dict()
