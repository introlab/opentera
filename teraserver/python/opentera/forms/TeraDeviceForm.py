from opentera.forms.TeraForm import *

from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from flask_babel import gettext


class TeraDeviceForm:

    @staticmethod
    def get_device_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("device")

        # Building lists
        #################
        # Device types & subtypes
        from opentera.db.models.TeraDeviceType import TeraDeviceType
        device_types = TeraDeviceType.get_devices_types()
        device_types_list = []
        for dev_type in device_types:
            name = gettext(dev_type.get_name())
            device_types_list.append(TeraFormValue(value_id=dev_type.id_device_type, value=name))

        # Sections
        section = TeraFormSection("details", gettext("Parameters"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_device", gettext("Device ID"), "hidden", item_required=True))
        section.add_item(TeraFormItem("device_uuid", gettext("Device UUID"), "hidden", item_required=True))
        section.add_item(TeraFormItem("device_name", gettext("Device Name"), "text", item_required=True))
        section.add_item(TeraFormItem("id_device_type", gettext("Device Type ID"), "array", item_required=True,
                                      item_values=device_types_list))
        section.add_item(TeraFormItem("id_device_subtype", gettext("Device Sub-Type"), "array", item_required=False,
                                      item_condition=TeraFormItemCondition("id_device_type", "=", "changed",
                                                                           "/api/user/devicesubtypes?id_device_type=")))
        section.add_item(TeraFormItem("device_token", gettext("Access Token"), "label",
                                      item_options={"readonly": False}))
        section.add_item(TeraFormItem("device_certificate", gettext("Certificate"), "hidden",
                                      item_options={"readonly": True}))
        section.add_item(TeraFormItem("device_enabled", gettext("Device Enabled?"), "boolean", item_required=True))
        section.add_item(TeraFormItem("device_onlineable", gettext("Device Onlineable?"), "boolean",
                                      item_required=True))

        section.add_item(TeraFormItem("device_lastonline", gettext("Last Connection"), "datetime",
                                      item_options={"readonly": True}))

        section3 = TeraFormSection("infos", gettext("Information"))
        form.add_section(section3)
        section3.add_item(TeraFormItem("device_infos", gettext("Device Information"), "longtext"))

        section2 = TeraFormSection("config", gettext("Configuration"))
        form.add_section(section2)
        section2.add_item(TeraFormItem("device_config", gettext("Device Configuration"), "longtext"))

        section1 = TeraFormSection("notes", gettext("Notes"))
        form.add_section(section1)
        section1.add_item(TeraFormItem("device_notes", gettext("Notes"), "longtext"))

        return form.to_dict()
