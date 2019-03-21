from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser


class OnlineUsers(Resource):

    def __init__(self, flaskModule):
        Resource.__init__(self)
        self.flaskModule = flaskModule
        self.parser = reqparse.RequestParser()

        # Register all callback for redis messages
        self.flaskModule.subscribe_pattern_with_callback('server.OnlineUsers.*', self.pattern_callback)

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = self.parser.parse_args()

        my_args = {}

        try:

            if self.flaskModule is not None:
                self.flaskModule.publish('api.OnlineUsers.' + session['user_id'] + '.request', b'list')

            users_list = []
            return jsonify(users_list)
        except InvalidRequestError:
            return '', 500

    def post(self):
        return '', 501

    def delete(self):
        return '', 501

    def pattern_callback(self, pattern, channel, data):
        print(self, 'pattern_callback', pattern, channel, data)
