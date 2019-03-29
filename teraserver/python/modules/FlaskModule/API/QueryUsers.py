from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser


class QueryUsers(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user_uuid', type=str, help='uuid')
        self.parser.add_argument('id_site', type=int, help='Users for a specific site')
        self.parser.add_argument('id_project', type=int, help='Users for a specific project')

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = self.parser.parse_args()

        # my_args = {}
        #
        # # Make sure we remove the None
        # for key in args:
        #     if args[key] is not None:
        #         my_args[key] = args[key]

        users = []
        # If we have no arguments, return all accessible users
        if not all(args.values()):
            users = current_user.get_accessible_users()

        # If we have a user_uuid, query for that user if accessible
        if args['user_uuid']:
            return current_user.query_user_for_uuid(args['user_uuid'])

        # If we have a id_site, query for users of that site, if accessible
        # TODO

        # If we have a id_project, query for users of that project, if accessible

        if users:
            users_list = []
            for user in users:
                users_list.append(user.to_json())
            return jsonify(users_list)

        return '', 500
        # try:
        #     users = TeraUser.query_data(my_args)
        #     users_list = []
        #     for user in users:
        #         users_list.append(user.to_json())
        #     return jsonify(users_list)
        # except InvalidRequestError:
        #     return '', 500

    def post(self):
        return '', 501

    def delete(self):
        return '', 501

