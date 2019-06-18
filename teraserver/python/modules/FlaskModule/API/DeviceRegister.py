from flask_restful import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule, current_device
from flask import request


class DeviceRegister(Resource):
    """
    Registration process requires a POST with a certificate signing request (CSR)
    Will return the certificate with newly created device UUID, but disabled.
    Administrators will need to put the device in a site and enable it before use.
    """
    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    def get(self):
        print(request)
        return '', 200

    def post(self):
        print(request)
        return '', 200
