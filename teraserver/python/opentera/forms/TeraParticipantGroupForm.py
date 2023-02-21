from opentera.forms.TeraForm import *
from flask_babel import gettext
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup


class TeraParticipantGroupForm:

    @staticmethod
    def get_participant_group_form(projects: list):
        form = TeraForm("group")

        # Building lists
        project_list = []
        for project in projects:
            project_list.append(TeraFormValue(value_id=project.id_project, value=project.project_name + ' [' +
                                                                                 project.project_site.site_name + ']'))
        # Sections
        section = TeraFormSection("informations", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_participant_group", gettext("Participant Group ID"), "hidden", True))
        section.add_item(TeraFormItem("participant_group_name", gettext("Participant Group Name"), "text", True))
        section.add_item(TeraFormItem("id_project", gettext("Project"), "array", True, item_values=project_list))
        section.add_item(TeraFormItem("project_name", gettext("Project Name"), "hidden"))

        return form.to_dict()
