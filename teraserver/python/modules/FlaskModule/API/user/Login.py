from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.LoginModule.LoginModule import http_auth


class Login(Resource):

    def __init__(self, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self)
        self.parser = reqparse.RequestParser()

    @http_auth.login_required
    def get(self):

        session.permanent = True

        # Redis key is handled in LoginModule
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']

        # Get user token key from redis
        from modules.Globals import TeraServerConstants
        token_key = self.module.redisGet(TeraServerConstants.RedisVar_UserTokenAPIKey)

        # Get token for user
        from libtera.db.models.TeraUser import TeraUser
        user_token = TeraUser.get_token_for_user(session['user_id'], token_key)

        # Return reply as json object
        reply = {"websocket_url": "wss://" + servername + ":" + str(port) + "/wss?id=" + session['_id'],
                 "user_uuid": session['user_id'],
                 "user_token": user_token}
        json_reply = jsonify(reply)

        return json_reply

    @http_auth.login_required
    def post(self):
        # Authentification using a form (typically) or a post request
        print("User Login using POST")
        return "TODO", 501
