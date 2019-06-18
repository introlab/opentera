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
            device_types_list.append(TeraFormValue(value_id=dev_type.id_device_type, value=dev_type.device_type_name))

        sites = user_access.get_accessible_sites()
        sites_list = []
        for site in sites:
            sites_list.append(TeraFormValue(value_id=site.id_site, value=site.site_name))

        # Sections
        section = TeraFormSection("informations", gettext("Informations"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_device", gettext("ID Appareil"), "hidden", item_required=True))
        section.add_item(TeraFormItem("device_uuid", gettext("UUID Appareil"), "hidden", item_required=True))
        section.add_item(TeraFormItem("device_name", gettext("Nom appareil"), "text", item_required=True))
        section.add_item(TeraFormItem("device_type", gettext("Type appareil"), "array", item_required=True,
                                      item_values=device_types_list))
        section.add_item(TeraFormItem("device_token", gettext("Jeton d'accès"), "label",
                                      item_options={"readonly": True}))
        section.add_item(TeraFormItem("device_certificate", gettext("Certificat"), "label",
                                      item_options={"readonly": True}))
        section.add_item(TeraFormItem("id_site", gettext("Site d'appartenance"), "array", item_required=False,
                                      item_values=sites_list))
        section.add_item(TeraFormItem("device_enabled", gettext("Activé?"), "boolean", item_required=True))
        section.add_item(TeraFormItem("device_onlineable", gettext("Peut se connecter?"), "boolean",
                                      item_required=True))
        section.add_item(TeraFormItem("device_notes", gettext("Notes"), "longtext"))
        section.add_item(TeraFormItem("device_lastonline", gettext("Dernière connexion"), "label",
                                      item_options={"readonly": True}))

        section2 = TeraFormSection("profile", gettext("Paramètres"))
        form.add_section(section2)
        section2.add_item(TeraFormItem("device_profile", gettext("Paramètres"), "longtext"))

        return form.to_dict()
