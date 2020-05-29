from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from sqlalchemy import exc
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user', type=int, help='ID of the user from which to request all projects roles')
get_parser.add_argument('id_user_group', type=int, help='ID of the user group from which to request all projects roles')
get_parser.add_argument('id_project', type=int, help='ID of the project from which to request all users groups roles')
get_parser.add_argument('admins', type=inputs.boolean,
                        help='Flag to limit to projects from which the user is an admin or '
                             'users in project that have the admin role')
get_parser.add_argument('with_sites', type=inputs.boolean, help='Include sites information for each project.')

post_parser = reqparse.RequestParser()
post_parser.add_argument('project_access', type=str, location='json',
                         help='Project access to create / update', required=True)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Project Access ID to delete', required=True)


class QueryProjectAccess(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get user roles for projects. Only one ID parameter required and supported at once.',
             responses={200: 'Success - returns list of users roles in projects',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error occured when loading project roles'})
    def get(self):
        parser = get_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
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
                access = user_access.query_project_access_for_user(user_id=user_id,
                                                                   admin_only=args['admins'] is not None)

        # Query access for user group
        if args['id_user_group']:
            if args['id_user_group'] in user_access.get_accessible_users_groups_ids():
                from libtera.db.models.TeraUserGroup import TeraUserGroup
                user_group = TeraUserGroup.get_user_group_by_id(args['id_user_group'])
                access = user_group.get_projects_roles()

        # Query access for project id
        if args['id_project']:
            project_id = args['id_project']
            access = user_access.query_access_for_project(project_id=project_id,
                                                           admin_only=args['admins'] is not None)

        if access is not None:
            access_list = []
            for project, project_role in access.items():
                filters = []
                if not args['with_sites']:
                    filters = ['id_site', 'site_name']
                proj_access_json = project.to_json(ignore_fields=filters)
                proj_access_json['project_role'] = project_role
                access_list.append(proj_access_json)
            return jsonify(access_list)

        # No access, but still fine
        return [], 200

    @user_multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='Create/update project access for an user.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify this project or user access (project admin access required)',
                        400: 'Badly formed JSON or missing fields(id_user_group or id_project) in the JSON body',
                        500: 'Database error'})
    def post(self):
        parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_projects = request.json['project_access']

        if not isinstance(json_projects, list):
            json_projects = [json_projects]

        # Validate if we have everything needed
        json_rval = []
        for json_project in json_projects:
            if 'id_user_group' not in json_project:
                return 'Missing id_user_group', 400
            if 'id_project' not in json_project:
                return 'Missing id_project', 400

            # Check if current user can change the access for that site
            if user_access.get_project_role(project_id=json_project['id_project']) != 'admin':
                return 'Forbidden', 403

            # Do the update!
            try:
                access = TeraProjectAccess.update_project_access(json_project['id_user_group'],
                                                                 json_project['id_project'],
                                                                 json_project['project_access_role'])
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

            # TODO: Publish update to everyone who is subscribed to site access update...
            if access:
                json_rval.append(access.to_json())

        return jsonify(json_rval)

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific project access',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete project access(only user who is admin in that project can '
                             'remove it)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        project_access = TeraProjectAccess.get_project_access_by_id(id_todel)
        if not project_access:
            return 'No project access to delete.', 500

        # Check if current user can delete
        if user_access.get_project_role(project_access.id_project) != 'admin':
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraProjectAccess.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
