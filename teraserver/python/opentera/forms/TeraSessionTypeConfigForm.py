from opentera.forms.TeraForm import *
from flask_babel import gettext
from opentera.db.models.TeraSessionType import TeraSessionType


class TeraSessionTypeConfigForm:

    @staticmethod
    def get_session_type_config_form(session_type: TeraSessionType):

        form = TeraForm("session_type_config")

        # session_type: TeraSessionType = TeraSessionType.get_session_type_by_id(id_session_type)
        # if session_type:
        if session_type.session_type_category == TeraSessionType.SessionCategoryEnum.SERVICE.value:
            # System services
            if session_type.session_type_service.service_system:
                if session_type.session_type_service.service_key == 'VideoRehabService':
                    # Sections
                    section = TeraFormSection("general", gettext("General configuration"))
                    form.add_section(section)
                    # Items
                    section.add_item(TeraFormItem("session_recordable", gettext("Allow session recording"),
                                                  "boolean", False, item_default=False))
        return form.to_dict()


