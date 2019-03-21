from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.redis.AsyncRedisSubscribeWait import AsyncRedisSubscribeWait


class OnlineUsers(Resource):
    def __init__(self, flaskModule):
        Resource.__init__(self)
        self.flaskModule = flaskModule
        self.parser = reqparse.RequestParser()

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = self.parser.parse_args()

        my_args = {}

        try:

            req = AsyncRedisSubscribeWait('server.OnlineUsers.' + session['user_id'] + '.*', self.flaskModule)
            req.listen()

            # Publish request
            self.flaskModule.publish('api.OnlineUsers.' + session['user_id'] + '.request', b'list')

            # Wait for answer, no timeout
            (pattern, channel, data) = req.wait()

            req.stop()

            print('event received', pattern, channel, data)

            return jsonify(data)
        except InvalidRequestError:
            return '', 500

    def post(self):
        return '', 501

    def delete(self):
        return '', 501

