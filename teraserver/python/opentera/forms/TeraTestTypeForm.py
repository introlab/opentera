from opentera.forms.TeraForm import *
from flask_babel import gettext
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class TeraTestTypeForm:

    @staticmethod
    def get_test_type_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("test_type")

        # Building lists
        services = user_access.get_accessible_services()
        services_list = []
        for service in services:
            services_list.append(TeraFormValue(value_id=service.id_service, value=service.service_name))

        # Sections
        section = TeraFormSection("informations", "")
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_test_type", gettext("Test Type ID"), "hidden", True))
        section.add_item(TeraFormItem("test_type_name", gettext("Name"), "text", True))
        section.add_item(TeraFormItem("id_service", gettext("Service"), "array", item_required=True,
                                      item_values=services_list)
                         )
        section.add_item(TeraFormItem("test_type_uuid", gettext("UUID"), "hidden", True))
        section.add_item(TeraFormItem("test_type_key", gettext("Unique Key"), "text", False))
        section.add_item(TeraFormItem("test_type_has_json_format", gettext("Expose JSON structure"), "boolean", False))
        section.add_item(TeraFormItem("test_type_has_web_format", gettext("Expose Web interface"), "boolean", False))
        section.add_item(TeraFormItem("test_type_has_web_editor", gettext("Expose Web editor"), "boolean", False))
        section.add_item(TeraFormItem("test_type_description", gettext("Description"), "longtext", False))

        return form.to_dict()
