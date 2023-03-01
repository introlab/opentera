from opentera.forms.TeraForm import *
from flask_babel import gettext
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup


class TeraParticipantForm:

    @staticmethod
    def get_participant_form(groups=None):
        if groups is None:
            groups = []

        form = TeraForm("participant")

        # Building lists
        # Generic list or not accessible participant (such as when creating a new one) - return all groups
        groups_list = []
        for group in groups:
            groups_list.append(TeraFormValue(value_id=group.id_participant_group, value=group.participant_group_name))

        # Sections
        section = TeraFormSection("informations", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_participant", gettext("Participant ID"), "hidden", True))
        section.add_item(TeraFormItem("id_project", gettext("Projet ID"), "hidden", True))
        # section.add_item(TeraFormItem("id_site", gettext("Site ID"), "hidden", True))
        section.add_item(TeraFormItem("participant_uuid", gettext("Participant UUID"), "hidden", True))
        section.add_item(TeraFormItem("participant_name", gettext("Participant Name"), "text", True))
        section.add_item(TeraFormItem("participant_email", gettext("Participant Email"), "text", False))
        section.add_item(TeraFormItem("id_participant_group", gettext("Participant Group"), "array", False,
                                      item_values=groups_list))
        section.add_item(TeraFormItem("participant_enabled", gettext("Participant Enabled"), "boolean", True,
                                      item_default=True))
        section.add_item(TeraFormItem("participant_token_enabled", gettext("Participant Token Login Enabled"),
                                      "boolean", True, item_default=False))
        section.add_item(TeraFormItem("participant_token", gettext("Participant Token"), "label", False,
                                      item_options={"readonly": False}))
        section.add_item(TeraFormItem("participant_login_enabled", gettext("Participant Login Enabled"),
                                      "boolean", True, item_default=False))
        section.add_item(TeraFormItem("participant_username", gettext("Participant Username"), "text", True,
                                      item_condition=TeraFormItemCondition("participant_login_enabled", "=", True)))
        section.add_item(
            TeraFormItem("participant_password", gettext("Participant Password"), "password",
                         item_options={"confirm": True},
                         item_condition=TeraFormItemCondition("participant_login_enabled", "=", True)))
        section.add_item(TeraFormItem("participant_lastonline", gettext("Last Connection"), "datetime",
                                      item_options={"readonly": True}))
        section.add_item(TeraFormItem("participant_lastsession", gettext("Last Session"), "datetime",
                                      item_options={"readonly": True}))

        return form.to_dict()
