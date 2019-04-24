from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth, db_man
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraProject import TeraProject
from libtera.db.DBManager import DBManager


class QueryProjects(Resource):

    def __init__(self, flaskModule = None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id_project', type=int, help='id_project')
        parser.add_argument('id_site', type=int, help='id_site')
        parser.add_argument('user_uuid', type=str, help='user_uuid')
        parser.add_argument('list', type=bool, help='Request list')

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()

        projects = []
        # If we have no arguments, return all accessible projects
        queried_user = current_user
        if not any(args.values()):
            projects = user_access.get_accessible_projects()

        # If we have a user_uuid, query for the site of that user
        if args['user_uuid']:
            queried_user = TeraUser.get_user_by_uuid(args['user_uuid'])
            if queried_user is not None:
                user_access = DBManager.userAccess(queried_user)
                projects = user_access.get_accessible_projects()

        # If we have a site id, query for projects of that site
        if args['id_site']:
            projects = user_access.query_projects_for_site(site_id=args['id_site'])

        try:
            projects_list = []

            for project in projects:
                if args['list'] is None:
                    project_json = project.to_json()
                    project_json['project_role'] = user_access.get_project_role(project)
                    projects_list.append(project_json)
                else:
                    projects_list.append(project.to_json(minimal=True))

            return jsonify(projects_list)
        except InvalidRequestError:
            return '', 500

    def post(self):
        return '', 501

    def delete(self):
        return '', 501

