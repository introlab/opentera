from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser


class QueryUsers(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user_username', type=str, help='username')
        self.parser.add_argument('user_uuid', type=str, help='uuid')

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
            users = TeraUser.query_data(my_args)
            users_list = []
            for user in users:
                users_list.append(user.to_json())
            return jsonify(users_list)
        except InvalidRequestError:
            return '', 500

    def post(self):
        return '', 501

    def delete(self):
        return '', 501



"""
# Queries
    @staticmethod
    @flask_app.route('/api/query/users', methods=['GET', 'POST', 'DELETE'])
    @auth.login_required
    def users():
        if request.method == 'GET':
            current_user = TeraUser.get_user_by_uuid(session['user_id'])
            # if not request.args:
            #     # Return current user information
            #     user = TeraUser.get_user_by_uuid(session['user_id'])
            #     return jsonify([user.to_json()])

            # Parse query items
            # TODO: Check access rights
            try:
                users = TeraUser.query_data(request.args.to_dict())
                users_list = []
                for user in users:
                    users_list.append(user.to_json())
                return jsonify(users_list)
            except InvalidRequestError:
                abort(500)

            return

        if request.method == 'POST':
            abort(501)

        if request.method == 'DELETE':
            abort(501)


"""