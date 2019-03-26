from flask import jsonify
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser


class Definitions(Resource):

    def __init__(self, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('type', type=str, help='Definition type required', required=True)

    @auth.login_required
    def get(self):
        args = self.parser.parse_args(strict=True)

        if args['type'] == 'profile':
            return jsonify(TeraUser.get_profile_def())

        if args['type'] == 'user':
            return jsonify(TeraUser.get_user_def())

        return 'Unknown definition type: ' + args['type'], 500
