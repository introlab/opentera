from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from sqlalchemy import exc
from modules.LoginModule.LoginModule import multi_auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.DBManager import DBManager


class QueryProjectAccess(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @multi_auth.login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id_user', type=int, help='User ID')
        parser.add_argument('id_project', type=int, help='Site ID')

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()

        access = None
        # If we have no arguments, return bad request
        if not any(args.values()):
            return "ProjectAccess: missing argument.", 400

        # Query access for user id
        if args['id_user']:
            user_id = args['id_user']

            if user_id in user_access.get_accessible_users_ids():
                access = user_access.query_project_access_for_user(user_id=user_id)

        # Query access for project id
        if args['id_project']:
            project_id = args['id_project']
            access = user_access.query_access_for_project(project_id=project_id)

        if access is not None:
            access_list = []
            for proj_access in access:
                if proj_access is not None:
                    access_list.append(proj_access.to_json())
            return jsonify(access_list)

        return 'Unknown error', 500

    @multi_auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('project_access', type=str, location='json', help='Project access to create / update',
                            required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_projects = request.json['project_access']

        if not isinstance(json_projects, list):
            json_projects = [json_projects]

        # Validate if we have everything needed
        json_rval = []
        for json_project in json_projects:
            if 'id_user' not in json_project:
                return 'Missing id_user', 400
            if 'id_project' not in json_project:
                return 'Missing id_project', 400

            # Check if current user can change the access for that site
            if user_access.get_project_role(project_id=json_project['id_project']) != 'admin':
                return 'Forbidden', 403

            # Do the update!
            try:
                access = TeraProjectAccess.update_project_access(json_project['id_user'], json_project['id_project'],
                                                                 json_project['project_access_role'])
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

            # TODO: Publish update to everyone who is subscribed to site access update...
            if access:
                json_rval.append(access.to_json())

        return jsonify(json_rval)

    @multi_auth.login_required
    def delete(self):

        return '', 501

