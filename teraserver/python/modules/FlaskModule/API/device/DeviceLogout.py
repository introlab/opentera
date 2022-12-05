from flask import jsonify, session
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_device
from flask_login import logout_user


class DeviceLogout(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @LoginModule.device_token_or_certificate_required
    def get(self):
        if current_device:
            logout_user()
            session.clear()
            self.module.send_device_disconnect_module_message(current_device.device_uuid)
            return gettext("Device logged out."), 200
        else:
            return gettext("Device not logged in"), 403

