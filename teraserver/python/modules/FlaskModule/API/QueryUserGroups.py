from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraUserGroup import TeraUserGroup


class QueryUserGroups(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule
        self.parser = reqparse.RequestParser()
        # self.parser.add_argument('user_username', type=str, help='username')
        # self.parser.add_argument('user_uuid', type=str, help='uuid')

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = self.parser.parse_args()

        my_args = {}

        # Make sure we remove the None, safe?
        for key in args:
            if args[key] is not None:
                my_args[key] = args[key]

        try:
            groups = TeraUserGroup.query_data(my_args)
            groups_list = []
            for group in groups:
                groups_list.append(group.to_json())
            return jsonify(groups_list)
        except InvalidRequestError:
            return '', 500

    def post(self):
        return '', 501

    def delete(self):
        return '', 501

