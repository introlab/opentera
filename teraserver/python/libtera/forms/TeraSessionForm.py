from libtera.forms.TeraForm import *
from flask_babel import gettext
from libtera.db.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from libtera.db.models.TeraSession import TeraSessionStatus


class TeraSessionForm:

    @staticmethod
    def get_session_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("session")

        # Building lists
        # Session types
        ses_types = user_access.get_accessible_session_types()
        st_list = []
        for st in ses_types:
            st_list.append(TeraFormValue(value_id=st.id_session_type, value=st.session_type_name))

        # Users
        users = user_access.get_accessible_users()
        users_list = []
        for user in users:
            users_list.append(TeraFormValue(value_id=user.id_user, value=user.get_fullname()))

        # Session status
        status_list = []
        for status in TeraSessionStatus:
            status_list.append(TeraFormValue(value_id=status.value, value=status.name))

        # Sections
        section = TeraFormSection("informations", gettext("Informations"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_session", gettext("ID séance"), "hidden", True))
        section.add_item(TeraFormItem("session_name", gettext("Nom de la séance"), "text", True))
        section.add_item(TeraFormItem("id_session_type", gettext("Type de séance"), "array", True, item_values=st_list))
        section.add_item(TeraFormItem("id_creator_user", gettext("Créateur"), "array", False, item_values=users_list))
        section.add_item(TeraFormItem("session_start_datetime", gettext("Date de début"), "datetime", True))
        section.add_item(TeraFormItem("session_duration", gettext("Durée"), "duration", True,
                                      item_options={"default": 0, "readonly": True}))
        # Session status is hidden as it needs to be handled elsewhere for now
        section.add_item(TeraFormItem("session_status", gettext("État"), "hidden", True, item_values=status_list))
        section.add_item(TeraFormItem("session_comments", gettext("Commentaires"), "longtext", False))

        return form.to_dict()
