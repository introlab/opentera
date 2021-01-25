from opentera.forms.TeraForm import *
from flask_babel import gettext


class TeraSiteForm:

    @staticmethod
    def get_site_form():
        form = TeraForm("site")

        # Sections
        section = TeraFormSection("informations", gettext("Information"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_site", gettext("Site ID"), "hidden", True))
        section.add_item(TeraFormItem("site_name", gettext("Site Name"), "text", True))
        section.add_item(TeraFormItem("site_role", gettext("Site Role"), "hidden", False))

        return form.to_dict()
