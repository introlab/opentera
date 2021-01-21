from opentera.forms.TeraForm import *
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
        section = TeraFormSection("informations", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_project", gettext("Project ID"), "hidden", True))
        section.add_item(TeraFormItem("project_name", gettext("Project Name"), "text", True))
        section.add_item(TeraFormItem("id_site", gettext("Site"), "array", True, item_values=sites_list))
        section.add_item(TeraFormItem("project_role", gettext("Role"), "hidden"))
        section.add_item(TeraFormItem("site_name", gettext("Site Name"), "hidden"))

        return form.to_dict()
