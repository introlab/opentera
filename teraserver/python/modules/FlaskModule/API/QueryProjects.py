from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth, db_man
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser


class QueryProjects(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id_project', type=int, help='id_project')
        self.parser.add_argument('id_site', type=int, help='id_site')
        self.parser.add_argument('user_uuid', type=str, help='user_uuid')

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = self.parser.parse_args()

        projects = []
        # If we have no arguments, return all accessible projects
        queried_user = current_user
        if not any(args.values()):
            projects = queried_user.get_accessible_projects()

        # If we have a user_uuid, query for the site of that user
        if args['user_uuid']:
            queried_user = TeraUser.get_user_by_uuid(args['user_uuid'])
            if queried_user is not None:
                projects = queried_user.get_accessible_projects()
        try:
            projects_list = []

            for project in projects:
                project_json = project.to_json()
                project_json['project_role'] = queried_user.get_project_role(project)
                projects_list.append(project_json)
            return jsonify(projects_list)
        except InvalidRequestError:
            return '', 500

    def post(self):
        return '', 501

    def delete(self):
        return '', 501

