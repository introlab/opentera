from opentera.forms.TeraForm import *
from flask_babel import gettext


class TeraSiteForm:

    @staticmethod
    def get_site_form(**kwargs):
        form = TeraForm("site")
        show_2fa_fields = kwargs.get('show_2fa_fields', True)

        # Sections
        section = TeraFormSection("informations", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_site", gettext("Site ID"), "hidden", True))
        section.add_item(TeraFormItem("site_name", gettext("Site Name"), "text", True))
        if show_2fa_fields:
            section.add_item(TeraFormItem("site_2fa_required", gettext("Users Require 2FA"), "boolean",
                                          False, item_default=False))
        section.add_item(TeraFormItem("site_role", gettext("Site Role"), "hidden", False))

        return form.to_dict()
