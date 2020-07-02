from libtera.forms.TeraForm import *

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
        section = TeraFormSection("infos", gettext("Informations"))
        form.add_section(section)

        # service_endpoint = db.Column(db.String, nullable=False)
        # service_clientendpoint = db.Column(db.String, nullable=False)
        # service_enabled = db.Column(db.Boolean, nullable=False, default=False)
        # Items
        section.add_item(TeraFormItem("id_service", gettext("ID Service"), "hidden", item_required=True))
        section.add_item(TeraFormItem("service_uuid", gettext("UUID Service"), "label", item_required=False,
                                      item_options={"readonly": False}))
        section.add_item(TeraFormItem("service_name", gettext("Nom du service"), "text", item_required=True))
        section.add_item(TeraFormItem("service_key", gettext("Code du service"), "text", item_required=True))
        section.add_item(TeraFormItem("service_hostname", gettext("Adresse interne"), "text", item_required=True))
        section.add_item(TeraFormItem("service_port", gettext("Port interne"), "numeric", item_required=True))
        section.add_item(TeraFormItem("service_endpoint", gettext("URL de base"), "text", item_required=True))
        section.add_item(TeraFormItem("service_clientendpoint", gettext("URL externe"), "text", item_required=True))
        section.add_item(TeraFormItem("service_enabled", gettext("Service actif"), "boolean", item_required=True))

        return form.to_dict()
