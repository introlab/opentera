from libtera.forms.TeraForm import *
from flask_babel import gettext
from libtera.db.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class TeraParticipantForm:

    @staticmethod
    def get_participant_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("participant")

        # Building lists
        groups = user_access.get_accessible_groups()
        groups_list = []
        for group in groups:
            groups_list.append(TeraFormValue(value_id=group.id_participant_group, value=group.participant_group_name))

        # Sections
        section = TeraFormSection("informations", gettext("Informations"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_participant", gettext("ID Participant"), "hidden", True))
        section.add_item(TeraFormItem("id_project", gettext("ID Projet"), "hidden", True))
        section.add_item(TeraFormItem("participant_uuid", gettext("UUID Participant"), "hidden", True))
        section.add_item(TeraFormItem("participant_name", gettext("Nom Participant"), "text", True))
        section.add_item(TeraFormItem("participant_enabled", gettext("Participant actif"), "boolean", True))
        section.add_item(TeraFormItem("participant_token", gettext("Jeton Participant"), "label", False,
                                      item_options={"readonly": True}))
        section.add_item(TeraFormItem("participant_lastonline", gettext("Dernière connexion"), "label",
                                      item_options={"readonly": True}))
        section.add_item(TeraFormItem("id_participant_group", gettext("Groupe"), "array", True,
                                      item_values=groups_list))

        return form.to_dict()
