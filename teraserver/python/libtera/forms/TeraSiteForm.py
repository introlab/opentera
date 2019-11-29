from libtera.forms.TeraForm import *
from flask_babel import gettext


class TeraSiteForm:

    @staticmethod
    def get_site_form():
        form = TeraForm("site")

        # Sections
        section = TeraFormSection("informations", gettext("Informations"))
        form.add_section(section)

        # Items
        section.add_item(TeraFormItem("id_site", gettext("ID Site"), "hidden", True))
        section.add_item(TeraFormItem("site_name", gettext("Nom du site"), "text", True))
        section.add_item(TeraFormItem("site_role", gettext("Rôle dans ce site"), "hidden", False))

        return form.to_dict()
