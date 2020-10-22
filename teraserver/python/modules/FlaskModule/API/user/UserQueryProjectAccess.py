from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from sqlalchemy import exc
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraServiceAccess import TeraServiceAccess
from libtera.db.models.TeraServiceRole import TeraServiceRole
from modules.DatabaseModule.DBManager import DBManager
import modules.Globals as Globals

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user', type=int, help='ID of the user from which to request all projects roles')
get_parser.add_argument('id_user_group', type=int, help='ID of the user group from which to request all projects roles')
get_parser.add_argument('id_project', type=int, help='ID of the project from which to request all users groups roles')
get_parser.add_argument('admins', type=inputs.boolean,
                        help='Flag to limit to projects from which the user is an admin or '
                             'users in project that have the admin role')
get_parser.add_argument('with_sites', type=inputs.boolean, help='Include sites information for each project.')
get_parser.add_argument('by_users', type=inputs.boolean, help='If specified, returns roles by users instead of by user'
                                                              'groups')
get_parser.add_argument('with_empty', type=inputs.boolean, help='Used with id_user_group. Also return projects that '
                                                                'don\'t have any access with that user group. Used with'
                                                                ' id_project. also return user groups that don\'t have '
                                                                'any access to the project')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('project_access', type=str, location='json',
#                          help='Project access to create / update', required=True)
post_schema = api.schema_model('user_project_access', {
    'properties': {
        'project_access': {
            'properties': {
                'id_project': {
                    'type': 'integer',
                    'required': True
                },
                'id_user_group': {
                    'type': 'integer',
                    'required': True
                },
                'project_access_role': {
                    'type': 'string'
                },
                'id_service_role': {
                    'type': 'integer'
                }
            }
        }
    },
    'type': 'object',
    'location': 'json'})


delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Project Access ID to delete', required=True)


class UserQueryProjectAccess(Resource):

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
        from libtera.db.models.TeraProject import TeraProject
        parser = get_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()

        access = None
        # If we have no arguments, return bad request
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        # Query access for user id
        if args['id_user']:
            user_id = args['id_user']

            if user_id in user_access.get_accessible_users_ids():
                access = user_access.query_project_access_for_user(user_id=user_id,
                                                                   admin_only=args['admins'])

        # Query access for user group
        if args['id_user_group']:
            if args['id_user_group'] in user_access.get_accessible_users_groups_ids():
                access = user_access.query_project_access_for_user_group(user_group_id=args['id_user_group'],
                                                                         admin_only=args['admins'],
                                                                         include_projects_without_access=
                                                                         args['with_empty']
                                                                         )

        # Query access for project id
        if args['id_project']:
            project_id = args['id_project']
            access = user_access.query_access_for_project(project_id=project_id,
                                                          admin_only=args['admins'],
                                                          include_empty_groups=args['with_empty'])

        if access is not None:
            access_list = []
            if not args['by_users'] or args['id_user']:
                for project, project_role in access.items():
                    filters = []
                    if not args['with_sites']:
                        filters = ['id_site', 'site_name']
                    proj_access_json = project.to_json(ignore_fields=filters)
                    if args['with_sites']:
                        if not args['id_project']:
                            current_project = project
                        else:
                            # When we have a id_project request, we have usergroups, not project here
                            current_project = TeraProject.get_project_by_id(args['id_project'])
                        proj_access_json['id_site'] = current_project.id_site
                        proj_access_json['site_name'] = current_project.project_site.site_name
                    if project_role:
                        proj_access_json['project_access_role'] = project_role['project_role']
                        if project_role['inherited']:
                            proj_access_json['project_access_inherited'] = True
                    else:
                        proj_access_json['project_access_role'] = None
                    access_list.append(proj_access_json)
            else:
                users_list = []
                projects_list = []
                if args['id_project']:
                    # We have user groups if we queried for a specific project
                    for usergroup, site_role in access.items():
                        users_list.extend(user_access.query_users_for_usergroup(user_group_id=usergroup.id_user_group))
                    projects_list = [TeraProject.get_project_by_id(args['id_project'])]

                if args['id_user_group']:
                    users_list = user_access.query_users_for_usergroup(user_group_id=args['id_user_group'])
                    projects_list = [project for project in access]

                for user in users_list:
                    if user.id_user not in [value['id_user'] for value in access_list]:
                        for project in projects_list:
                            project_role = user_access.get_user_project_role(user_id=user.id_user,
                                                                             project_id=project.id_project)
                            if args['admins'] and project_role and project_role['project_role'] != 'admin':
                                site_role = None
                            project_access_json = {'id_user': user.id_user,
                                                   'id_project': project.id_project,
                                                   'user_name': user.get_fullname(),
                                                   'project_access_role': project_role['project_role']
                                                   if project_role else None,
                                                   'project_access_inherited': project_role['inherited']
                                                   if project_role else None
                                                   }
                            if args['with_sites']:
                                project_access_json['id_site'] = project.id_site
                                project_access_json['site_name'] = project.project_site.site_name
                            if project_access_json:
                                access_list.append(project_access_json)

            return access_list

        # No access, but still fine
        return [], 200

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create/update project access for an user.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify this project or user access (project admin access required)',
                        400: 'Badly formed JSON or missing fields(id_user_group or id_project) in the JSON body',
                        500: 'Database error'})
    def post(self):
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
                return gettext('Missing id_user_group'), 400
            if 'id_project' not in json_project:
                return gettext('Missing id_project'), 400
            if 'project_access_role' not in json_project and 'id_project_role' not in json_project:
                return gettext('Missing role name or id'), 400

            # Check if current user can change the access for that project
            if user_access.get_project_role(project_id=json_project['id_project']) != 'admin':
                return gettext('Forbidden'), 403

            project_service_role = None
            if 'project_access_role' in json_project:
                # Check if we must remove access for that site
                if json_project['project_access_role'] == '':
                    # No more access to that project for that user group - remove all access!
                    TeraServiceAccess.delete_service_access_for_user_group_for_project(
                        id_user_group=json_project['id_user_group'], id_project=json_project['id_project'])
                    continue

                # Find id_service_role for that
                project_service_role = \
                    TeraServiceRole.get_specific_service_role_for_project(service_id=Globals.opentera_service_id,
                                                                          project_id=json_project['id_project'],
                                                                          rolename=json_project['project_access_role'])
            if 'id_service_role' in json_project:
                if json_project['id_service_role'] == 0:
                    # No more access to that project for that user group - remove all access!
                    TeraServiceAccess.delete_service_access_for_user_group_for_project(
                        id_user_group=json_project['id_user_group'], id_project=json_project['id_project'])
                    continue
                project_service_role = TeraServiceRole.get_service_role_by_id(json_project['id_service_role'])

            if not project_service_role:
                return gettext('Invalid role name or id for that project'), 400

            # Do the update!
            try:
                # access = TeraProjectAccess.update_project_access(json_project['id_user_group'],
                #                                                  json_project['id_project'],
                #                                                  json_project['project_access_role'])
                access = TeraServiceAccess.update_service_access_for_user_group_for_project(
                    id_service=Globals.opentera_service_id, id_user_group=json_project['id_user_group'],
                    id_service_role=project_service_role.id_service_role, id_project=json_project['id_project'])
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryProjectAccess.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

            if access:
                json_access = access.to_json()
                # For backwards compatibility with "old" API
                json_access['id_project_access'] = access.id_service_access
                json_access['project_access_role'] = access.service_access_role.service_role_name
                json_rval.append(json_access)

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

        project_access = TeraServiceAccess.get_service_access_by_id(id_todel)
        if not project_access:
            return gettext('No project access to delete.'), 400

        # Check if current user can delete
        if user_access.get_project_role(project_access.service_access_role.id_project) != 'admin':
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceAccess.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryProjectAccess.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
