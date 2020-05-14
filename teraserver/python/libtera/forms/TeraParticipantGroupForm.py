from libtera.forms.TeraForm import *
from flask_babel import gettext
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class TeraParticipantGroupForm:

    @staticmethod
    def get_participant_group_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("group")

        # Building lists
        projects = user_access.get_accessible_projects()
        project_list = []
        for project in projects:
            project_list.append(TeraFormValue(value_id=project.id_project, value=project.project_name + ' [' +
                                                                                 project.project_site.site_name +
                                                                                 ']'))
        # Sections
        section = TeraFormSection("informations", gettext("Informations"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_participant_group", gettext("ID Groupe Participant"), "hidden", True))
        section.add_item(TeraFormItem("participant_group_name", gettext("Nom du groupe"), "text", True))
        section.add_item(TeraFormItem("id_project", gettext("Projet"), "array", True, item_values=project_list))
        section.add_item(TeraFormItem("project_name", gettext("Nom du projet"), "hidden"))

        return form.to_dict()
