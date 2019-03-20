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
        # print('Setting key with expiration in 60s', session['_id'], session['user_id'])
        # get_redis().set(session['_id'], session['user_id'], ex=60)
        reply = {"websocket_url": "wss://localhost:4040/wss?id=" + session['_id'],
                 "user_uuid": session['user_id']}
        json_reply = jsonify(reply)

        return json_reply
