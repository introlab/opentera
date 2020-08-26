from libtera.forms.TeraForm import *


from flask_babel import gettext


class TeraServiceConfigForm:

    @staticmethod
    def get_service_config_form():
        form = TeraForm("service_config")

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
        section.add_item(TeraFormItem("id_service_config", gettext("Service Config ID"), "hidden", item_required=True))
        section.add_item(TeraFormItem("id_user", gettext("User ID"), "hidden", item_required=False))
        section.add_item(TeraFormItem("id_device", gettext("Device ID"), "hidden", item_required=False))
        section.add_item(TeraFormItem("id_participant", gettext("Participant ID"), "hidden", item_required=False))
        section.add_item(TeraFormItem("service_config_config", gettext("Service Config"), "hidden", item_required=True))

        form_dict = form.to_dict()

        # if service.has_config_schema():
        #     import json
        #     config_json = json.loads(service.service_config_schema)
        #     form_dict.update(config_json)

        return form_dict
