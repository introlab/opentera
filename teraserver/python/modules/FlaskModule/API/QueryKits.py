from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from sqlalchemy.exc import InvalidRequestError


class QueryKits(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id_kit', type=int, help='id_kit')
        self.parser.add_argument('kit_name', type=str, help='kit_name')

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = self.parser.parse_args()

        kits = []
        # If we have no arguments, return all accessible devices
        try:
            if not any(args.values()):
                kits = current_user.get_accessible_kits()

            kit_list = []
            for kit in kits:
                kit_json = kit.to_json()
                kit_list.append(kit_json)
            return jsonify(kit_list)

        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        return '', 501

    @auth.login_required
    def delete(self):
        return '', 501
