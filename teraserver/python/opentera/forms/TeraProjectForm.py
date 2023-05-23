from opentera.forms.TeraForm import *
from flask_babel import gettext
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class TeraProjectForm:

    @staticmethod
    def get_project_form(accessible_sites: list):
        form = TeraForm("project")

        # Building lists
        sites_list = []
        for site in accessible_sites:
            sites_list.append(TeraFormValue(value_id=site.id_site, value=site.site_name))

        # Sections
        section = TeraFormSection("informations", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_project", gettext("Project ID"), "hidden", item_required=True))
        section.add_item(TeraFormItem("project_name", gettext("Project Name"), "text", item_required=True))
        section.add_item(TeraFormItem("project_enabled", gettext("Enabled"), "boolean", item_required=True,
                                      item_default=True))
        section.add_item(TeraFormItem("id_site", gettext("Site"), "array", item_required=True, item_values=sites_list))
        section.add_item(TeraFormItem("project_role", gettext("Role"), "hidden"))
        section.add_item(TeraFormItem("site_name", gettext("Site Name"), "hidden"))

        desc_section = TeraFormSection("description", gettext("Description"))
        form.add_section(desc_section)
        desc_section.add_item(TeraFormItem("project_description", gettext("Description"), "longtext",
                                           item_required=False))

        return form.to_dict()
