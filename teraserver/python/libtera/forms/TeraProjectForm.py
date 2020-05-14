from libtera.forms.TeraForm import *
from flask_babel import gettext
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class TeraProjectForm:

    @staticmethod
    def get_project_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("project")

        # Building lists
        sites = user_access.get_accessible_sites()
        sites_list = []
        for site in sites:
            sites_list.append(TeraFormValue(value_id=site.id_site, value=site.site_name))

        # Sections
        section = TeraFormSection("informations", gettext("Informations"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_project", gettext("ID Projet"), "hidden", True))
        section.add_item(TeraFormItem("project_name", gettext("Nom du projet"), "text", True))
        section.add_item(TeraFormItem("id_site", gettext("Site"), "array", True, item_values=sites_list))
        section.add_item(TeraFormItem("project_role", gettext("Rôle"), "hidden"))
        section.add_item(TeraFormItem("site_name", gettext("Nom du site initial"), "hidden"))

        return form.to_dict()
