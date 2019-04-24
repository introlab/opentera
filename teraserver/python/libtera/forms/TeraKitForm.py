from libtera.forms.TeraForm import *
from flask_babel import gettext
from libtera.db.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class TeraKitForm:

    @staticmethod
    def get_kit_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("kit")

        # Building lists
        sites = user_access.get_accessible_sites()
        sites_list = []
        for site in sites:
            sites_list.append(TeraFormValue(value_id=site.id_site, value=site.site_name))

        projects = user_access.get_accessible_projects()
        projects_list = []
        for project in projects:
            projects_list.append(TeraFormValue(value_id=project.id_project, value=project.project_name))

        # Sections
        section = TeraFormSection("informations", gettext("Informations"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_kit", gettext("ID Kit"), "hidden", True))
        section.add_item(TeraFormItem("kit_name", gettext("Nom du kit"), "text", True))
        section.add_item(TeraFormItem("id_site", gettext("Site"), "array", True, item_values=sites_list))
        section.add_item(TeraFormItem("id_project", gettext("Projet"), "array", item_values=projects_list))
        section.add_item(TeraFormItem("kit_shareable", gettext("Kit partageable?"), "boolean", True))
        section.add_item(TeraFormItem("kit_lastonline", gettext("Dernière connexion"), "label",
                                      item_options={"readonly": True}))

        return form.to_dict()
