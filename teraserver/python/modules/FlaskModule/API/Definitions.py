from flask import jsonify
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser


class Definitions(Resource):

    def __init__(self, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('type', type=str, help='Definition type required')

    @auth.login_required
    def get(self):
        args = self.parser.parse_args(strict=True)

        if args['type'] is None:
            return 'No definition type specified', 500

        if args['type'] == 'profile':
            profile_def = TeraUser.get_profile_def()
            return jsonify(profile_def)

        return 'Unknown definition type: ' + args['type'], 500
