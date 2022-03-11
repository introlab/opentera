from flask import jsonify, session
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_device
from modules.DatabaseModule.DBManager import DBManager
from modules.FlaskModule.FlaskModule import device_api_ns as api


class DeviceLogout(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @LoginModule.device_token_or_certificate_required
    def get(self):
        return gettext("Forbidden"), 403

