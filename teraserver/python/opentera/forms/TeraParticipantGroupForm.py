from opentera.forms.TeraForm import *
from flask_babel import gettext
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup


class TeraParticipantGroupForm:

    @staticmethod
    def get_participant_group_form(user_access: DBManagerTeraUserAccess, specific_group_id: int = None,
                                   site_id: int = None):
        form = TeraForm("group")

        # Building lists
        projects = []
        if site_id:
            # Specific project id specified
            projects = user_access.query_projects_for_site(site_id=site_id)
        elif not specific_group_id or specific_group_id not in user_access.get_accessible_groups_ids():
            # No specific group id specified
            projects = user_access.get_accessible_projects()
        else:
            # Specific group id specified
            group = TeraParticipantGroup.get_participant_group_by_id(specific_group_id)
            if group:
                projects = user_access.query_projects_for_site(group.participant_group_project.id_site)

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
