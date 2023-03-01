from opentera.forms.TeraForm import *
from flask_babel import gettext
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class TeraUserForm:

    @staticmethod
    def get_user_form():
        form = TeraForm("user")

        # Sections
        section = TeraFormSection("informations", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_user", gettext("User ID"), "hidden", True))
        section.add_item(TeraFormItem("user_uuid", gettext("User UUID"), "hidden"))
        section.add_item(TeraFormItem("user_name", gettext("User Full Name"), "hidden"))
        section.add_item(TeraFormItem("user_username", gettext("Username"), "text", True))
        section.add_item(TeraFormItem("user_enabled", gettext("User Enabled"), "boolean", True, item_default=True))
        section.add_item(TeraFormItem("user_firstname", gettext("First Name"), "text", True))
        section.add_item(TeraFormItem("user_lastname", gettext("Last Name"), "text", True))
        section.add_item(TeraFormItem("user_email", gettext("Email"), "text"))
        section.add_item(
            TeraFormItem("user_password", gettext("Password"), "password", item_options={"confirm": True}))
        section.add_item(TeraFormItem("user_superadmin", gettext("User Is Super Administrator"), "boolean", True))
        section.add_item(TeraFormItem("user_notes", gettext("Notes"), "longtext"))
        section.add_item(TeraFormItem("user_profile", gettext("Profile"), "hidden"))
        section.add_item(TeraFormItem("user_lastonline", gettext("Last Connection"), "datetime",
                                      item_options={"readonly": True}))

        return form.to_dict()
