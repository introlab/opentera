from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule, current_device


class DeviceLogin(Resource):

    def __init__(self, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self)
        self.parser = reqparse.RequestParser()

    @LoginModule.certificate_required
    def get(self):

        # Redis key is handled in LoginModule
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']

        # TODO Handle sessions
        if current_device.device_onlineable:
            # Permanent ?
            session.permanent = True

            # Return reply as json object
            reply = {"websocket_url": "wss://" + servername + ":" + str(port) + "/wss?id=" + session['_id'],
                     "device_info": current_device.to_json()}

            json_reply = jsonify(reply)

            return json_reply

        else:

            # Return reply as json object
            reply = {"device_info": current_device.to_json()}

            json_reply = jsonify(reply)

            return json_reply
