from flask import jsonify, session, request
from flask_restplus import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule, current_device
from modules.Globals import db_man
from modules.FlaskModule.FlaskModule import device_api_ns as api


class DeviceQueryAssets(Resource):

    def __init__(self, _api, flaskModule=None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @LoginModule.token_or_certificate_required
    def get(self):
        return '', 501

    @LoginModule.token_or_certificate_required
    def post(self):
        return '', 501
