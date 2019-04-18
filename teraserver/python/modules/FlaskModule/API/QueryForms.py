from flask import jsonify
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.forms.TeraUserForm import *
from libtera.forms.TeraSiteForm import *


class QueryForms(Resource):

    def __init__(self, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('type', type=str, help='Definition type required', required=True)

    @auth.login_required
    def get(self):
        args = self.parser.parse_args(strict=True)

        if args['type'] == 'user_profile':
            return jsonify(TeraUserForm.get_user_profile_definition())

        if args['type'] == 'user':
            return jsonify(TeraUserForm.get_user_definition())

        if args['type'] == 'site':
            return jsonify(TeraSiteForm.get_site_definition())

        return 'Unknown definition type: ' + args['type'], 500
