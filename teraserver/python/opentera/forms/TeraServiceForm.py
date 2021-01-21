from opentera.forms.TeraForm import *

from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from flask_babel import gettext


class TeraServiceForm:

    @staticmethod
    def get_service_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("service")

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
        section.add_item(TeraFormItem("service_uuid", gettext("Service UUID"), "label", item_required=False,
                                      item_options={"readonly": False}))
        section.add_item(TeraFormItem("service_name", gettext("Service Name"), "text", item_required=True))
        section.add_item(TeraFormItem("service_key", gettext("Service Key"), "text", item_required=True))
        section.add_item(TeraFormItem("service_hostname", gettext("Service Hostname"), "text", item_required=True))
        section.add_item(TeraFormItem("service_port", gettext("Service Internal Port"), "numeric", item_required=True))
        section.add_item(TeraFormItem("service_endpoint", gettext("Service Internal URL"), "text", item_required=True))
        section.add_item(TeraFormItem("service_clientendpoint", gettext("Service External Endpoint"), "text",
                                      item_required=True))
        section.add_item(TeraFormItem("service_endpoint_user", gettext("Service User Endpoint"), "text",
                                      item_required=False))
        section.add_item(TeraFormItem("service_endpoint_participant", gettext("Service Participant Endpoint"), "text",
                                      item_required=False))
        section.add_item(TeraFormItem("service_endpoint_device", gettext("Service Device Endpoint"), "text",
                                      item_required=False))
        section.add_item(TeraFormItem("service_enabled", gettext("Service Enabled"), "boolean", item_required=True))
        section.add_item(TeraFormItem("service_editable_config", gettext("Service has editable config"), "boolean",
                                      item_required=False))
        section.add_item(TeraFormItem("service_default_config", gettext("Service Default Configuration"), "longtext",
                                      item_required=False))

        return form.to_dict()
