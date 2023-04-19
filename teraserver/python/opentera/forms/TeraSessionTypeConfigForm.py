from opentera.forms.TeraForm import *
from flask_babel import gettext
from opentera.db.models.TeraSessionType import TeraSessionType


class TeraSessionTypeConfigForm:

    @staticmethod
    def get_session_type_config_form(session_type: TeraSessionType):
        # Handle session type configs for non-services session types
        form = TeraForm("session_type_config")
        return form.to_dict()


