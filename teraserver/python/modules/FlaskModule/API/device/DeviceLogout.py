from flask import jsonify, session
from flask_restplus import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule, current_device
from modules.Globals import db_man
from modules.FlaskModule.FlaskModule import device_api_ns as api


class DeviceLogout(Resource):

    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)
        self.parser = reqparse.RequestParser()

    @LoginModule.device_token_or_certificate_required
    def get(self):
        return "Forbidden", 403

