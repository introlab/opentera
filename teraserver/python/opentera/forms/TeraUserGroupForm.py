from opentera.forms.TeraForm import *

from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from flask_babel import gettext


class TeraUserGroupForm:

    @staticmethod
    def get_user_group_form(user_access: DBManagerTeraUserAccess):
        form = TeraForm("user_group")

        # Building lists
        #################
        # None to build!

        # Sections
        section = TeraFormSection("infos", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_user_group", gettext("User Group ID"), "hidden",
                                      item_required=True))
        section.add_item(TeraFormItem("user_group_name", gettext("User Group Name"), "text",
                                      item_required=True))

        return form.to_dict()
