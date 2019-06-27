from flask_restful import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule, current_device
from flask import request

class DeviceUpload(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @LoginModule.certificate_required
    def get(self):
        print(request)
        print('current_device', current_device)
        return '', 200

    @LoginModule.certificate_required
    def post(self):
        print(request)
        print('current_device', current_device)
        return '', 200

