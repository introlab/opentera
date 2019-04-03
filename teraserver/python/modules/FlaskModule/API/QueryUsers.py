from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from sqlalchemy import exc
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
import json


class QueryUsers(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_uuid', type=str, help='uuid')
        parser.add_argument('id_site', type=int, help='Users for a specific site')
        parser.add_argument('id_project', type=int, help='Users for a specific project')

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = parser.parse_args()

        users = []
        # If we have no arguments, return all accessible users
        if not any(args.values()):
            users = current_user.get_accessible_users()

        # If we have a user_uuid, query for that user if accessible
        if args['user_uuid']:
            users.append(current_user.get_user_by_uuid(args['user_uuid']))

        # If we have a id_site, query for users of that site, if accessible
        # TODO

        # If we have a id_project, query for users of that project, if accessible
        # TODO

        if users:
            users_list = []
            for user in users:
                if user is not None:
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

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user', type=str, location='json', help='User to create / update', required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        # Using request.json instead of parser, since parser messes up the json!
        json_user = request.json['user']

        # Check if current user can modify the posted user
        if 'id_user' not in json_user or json_user['id_user'] not in current_user.get_accessible_users_ids():
            return '', 403

        # Do the update!
        try:
            TeraUser.update_user(json_user['id_user'], json_user)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return '', 500

        # TODO: Publish update to everyone who is subscribed to users update...
        update_user = TeraUser.get_user_by_id(json_user['id_user'])

        return jsonify([update_user.to_json()])

    @auth.login_required
    def delete(self):
        return '', 501

