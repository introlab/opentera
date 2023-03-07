from opentera.forms.TeraForm import *

from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from flask_babel import gettext


class TeraDeviceTypeForm:

    @staticmethod
    def get_device_type_form():
        form = TeraForm("device_type")

        # Building lists
        #################

        # Sections
        section = TeraFormSection("infos", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_device_type", gettext("Device Type ID"), "hidden",
                                      item_required=True))
        section.add_item(TeraFormItem("device_type_name", gettext("Device Type Name"), "text",
                                      item_required=True))
        section.add_item(TeraFormItem("device_type_key", gettext("Device Type Key"), "text",
                                      item_required=True))

        return form.to_dict()
