from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.Globals import auth
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
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
        parser.add_argument('id', type=int)
        parser.add_argument('id_site', type=int, help='id_site')
        parser.add_argument('user_uuid', type=str, help='user_uuid')
        parser.add_argument('list', type=bool, help='Request list')

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()

        projects = []
        # If we have no arguments, return all accessible projects
        # queried_user = current_user
        if not any(args.values()):
            projects = user_access.get_accessible_projects()

        if args['id']:
            args['id_project'] = args['id']

        if args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                projects = [TeraProject.get_project_by_id(args['id_project'])]

        elif args['user_uuid']:
            # If we have a user_uuid, query for the site of that user
            queried_user = TeraUser.get_user_by_uuid(args['user_uuid'])
            if queried_user is not None:
                user_access = DBManager.userAccess(queried_user)
                projects = user_access.get_accessible_projects()
        elif args['id_site']:
            # If we have a site id, query for projects of that site
            projects = user_access.query_projects_for_site(site_id=args['id_site'])

        try:
            projects_list = []

            for project in projects:
                if args['list'] is None:
                    project_json = project.to_json()
                    project_json['project_role'] = user_access.get_project_role(project.id_project)
                    projects_list.append(project_json)
                else:
                    projects_list.append(project.to_json(minimal=True))

            return jsonify(projects_list)
        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('project', type=str, location='json', help='Project to create / update', required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_project = request.json['project']

        # Validate if we have an id
        if 'id_project' not in json_project or 'id_site' not in json_project:
            return '', 400

        # Check if current user can modify the posted kit
        # User can modify or add a kit if it is the site admin of that kit
        if json_project['id_project'] not in user_access.get_accessible_projects_ids(admin_only=True) and \
                json_project['id_project'] > 0:
            return '', 403

        # Only site admins can create new projects
        if json_project['id_project'] == 0 and \
                json_project['id_site'] not in user_access.get_accessible_sites_ids(admin_only=True):
            return '', 403

        # Do the update!
        if json_project['id_project'] > 0:
            # Already existing
            try:
                TeraProject.update_project(json_project['id_project'], json_project)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_project = TeraProject()
                new_project.from_json(json_project)
                TeraProject.insert_project(new_project)
                # Update ID for further use
                json_project['id_project'] = new_project.id_project
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_project = TeraProject.get_project_by_id(json_project['id_project'])

        return jsonify([update_project.to_json()])

    @auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # Only site admins can delete a project
        project = TeraProject.get_project_by_id(id_todel)

        if user_access.get_site_role(project.project_site.id_site) != 'admin':
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraProject.delete_project(id_project=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200

