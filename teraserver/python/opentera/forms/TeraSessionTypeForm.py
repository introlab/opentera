from opentera.forms.TeraForm import *
from flask_babel import gettext
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from opentera.db.models.TeraSessionType import TeraSessionType


class TeraSessionTypeForm:

    @staticmethod
    def get_session_type_form(services: list):
        form = TeraForm("session_type")

        # Building lists
        categories = TeraSessionType.SessionCategoryEnum
        categories_list = []
        for category in categories:
            name = gettext(TeraSessionType.get_category_name(category))
            categories_list.append(TeraFormValue(value_id=category.value, value=name))

        services_list = []
        for service in services:
            services_list.append(TeraFormValue(value_id=service.id_service, value=service.service_name))

        # Sections
        section = TeraFormSection("informations", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_session_type", gettext("Session Type ID"), "hidden", True))
        section.add_item(TeraFormItem("session_type_name", gettext("Session Type Name"), "text", True))
        # section.add_item(TeraFormItem("session_type_prefix", gettext("Session Type Prefix"), "text", True,
        #                               item_options={'max_length': 10}))
        section.add_item(TeraFormItem("session_type_category", gettext("Category"), "array", item_required=True,
                                      item_values=categories_list))
        section.add_item(TeraFormItem("id_service", gettext("Service"), "array", item_required=False,
                                      item_values=services_list,
                                      item_condition= TeraFormItemCondition("session_type_category", "=",
                                                                            TeraSessionType.SessionCategoryEnum.SERVICE
                                                                            .value)
                                      )
                         )
        section.add_item(TeraFormItem("session_type_service_key", gettext("Session Type Service Key"), "hidden", False))
        section.add_item(TeraFormItem("session_type_online", gettext("Session Type Online"), "boolean", True))
        section.add_item(TeraFormItem("session_type_color", gettext("Session Type Display Color"), "color", True))
        section.add_item(TeraFormItem("session_type_config", gettext("Session Type Configuration"), "longtext", False))

        return form.to_dict()
