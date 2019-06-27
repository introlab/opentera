from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth


class Login(Resource):

    def __init__(self, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self)
        self.parser = reqparse.RequestParser()

    @auth.login_required
    def get(self):

        session.permanent = True

        # Redis key is handled in LoginModule
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']

        # Return reply as json object
        reply = {"websocket_url": "wss://" + servername + ":" + str(port) + "/wss?id=" + session['_id'],
                 "user_uuid": session['user_id']}
        json_reply = jsonify(reply)

        return json_reply
