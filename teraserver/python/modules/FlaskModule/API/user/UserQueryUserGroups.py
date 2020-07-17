from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from sqlalchemy import exc
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraServiceAccess import TeraServiceAccess
from libtera.db.models.TeraServiceRole import TeraServiceRole
from libtera.db.models.TeraUserGroup import TeraUserGroup
from flask_babel import gettext
from modules.DatabaseModule.DBManager import DBManager
import modules.Globals as Globals

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user_group', type=int, help='ID of the user group to query')
get_parser.add_argument('id_user', type=int, help='ID of the user to get all user groups')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('user_group', type=str, location='json', help='User group to create / update', required=True)
post_schema = api.schema_model('user_user_group', {'properties': TeraUserGroup.get_json_schema(),
                                                   'type': 'object',
                                                   'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='User group ID to delete', required=True)


class UserQueryUserGroups(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get user group information. If no id specified, returns all accessible users groups',
             responses={200: 'Success',
                        500: 'Database error'})
    def get(self):
        parser = get_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        args = parser.parse_args()

        user_access = DBManager.userAccess(current_user)

        user_groups = []

        if args['id_user_group']:
            if args['id_user_group'] in user_access.get_accessible_users_groups_ids():
                user_groups.append(TeraUserGroup.get_user_group_by_id(args['id_user_group']))
        elif args['id_user']:
            if args['id_user'] in user_access.get_accessible_users_ids():
                user = TeraUser.get_user_by_id(args['id_user'])
                user_groups = user.user_user_groups
        else:
            # If we have no arguments, return all accessible user groups
            user_groups = user_access.get_accessible_users_groups()

        if user_groups:
            user_groups_list = []
            for group in user_groups:
                if group is not None:
                    group_json = group.to_json(minimal=args['list'])
                    sites_list = []
                    for site in group.user_group_sites_access:
                        sites_list.append(site.to_json())
                    group_json['user_group_sites_access'] = sites_list
                    projects_list = []
                    for project in group.user_group_projects_access:
                        projects_list.append(project.to_json())
                    group_json['user_group_projects_access'] = projects_list
                    user_groups_list.append(group_json)
            return jsonify(user_groups_list)
        return [], 200

    @user_multi_auth.login_required
    # @api.expect(post_parser)
    @api.expect(post_schema)
    @api.doc(description='Create / update user group. id_user_group must be set to "0" to create a new user group. User'
                         ' groups can be modified has a site admin role.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified user group',
                        400: 'Badly formed JSON or missing field(id_user_group) in the JSON body',
                        500: 'Internal error when saving user group'})
    def post(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])

        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_user_group = request.json['user_group']

        # Validate if we have an id_user_group
        if 'id_user_group' not in json_user_group:
            return '', 400

        # Check if current user has at least an accessible site as admin
        current_user_sites = user_access.get_accessible_sites(admin_only=True)
        if not current_user_sites:
            return '', 403

        # Check if we have site access to handle separately
        json_sites = None
        if 'user_group_sites_access' in json_user_group:
            json_sites = json_user_group.pop('user_group_sites_access')

        # If user is not super admin, we must add site access to at least one of the current user's site where he is
        # admin to allow further modification on user groups
        if not json_sites and not current_user.user_superadmin:
            site = {'id_site': current_user_sites[0].id_site, 'site_access_role': 'user'}
            json_sites = [site]

        # Check if we have project access to handle separately
        json_projects = None
        if 'user_group_projects_access' in json_user_group:
            json_projects = json_user_group.pop('user_group_projects_access')

        # Do the update!
        if json_user_group['id_user_group'] > 0:
            # Already existing user group
            try:
                TeraUserGroup.update(json_user_group['id_user_group'], json_user_group)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # Creates a new user group
            try:
                new_user_group = TeraUserGroup()
                new_user_group.from_json(json_user_group)
                TeraUserGroup.insert(new_user_group)
                # Update ID User Group for further use
                json_user_group['id_user_group'] = new_user_group.id_user_group
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        if json_sites:
            for site in json_sites:
                # Check if current user is admin of that site, if not, ignore it...
                if user_access.get_site_role(site_id=site['id_site']) == 'admin':
                    try:
                        # Check if we must remove access for that site
                        if site['site_role'] == '':
                            # No more access to that site for that user group - remove all access!
                            TeraServiceAccess.delete_service_access_for_user_group_for_site(
                                id_user_group=json_user_group['id_user_group'], id_site=int(site['id_site']))
                            continue

                        # Find id_service_role
                        site_service_role = \
                            TeraServiceRole.get_specific_service_role_for_site(service_id=Globals.opentera_service_id,
                                                                               site_id=int(site['id_site']),
                                                                               rolename=site['site_role'])
                        TeraServiceAccess.update_service_access_for_user_group_for_site(
                            id_service=Globals.opentera_service_id, id_user_group=json_user_group['id_user_group'],
                            id_service_role=site_service_role.id_service_role, id_site=int(site['id_site']))
                    except exc.SQLAlchemyError:
                        import sys
                        print(sys.exc_info())
                        return '', 500

        if json_projects:
            for project in json_projects:
                # Check if current user is admin of that project
                if user_access.get_project_role(project_id=project['id_project']) == 'admin':
                    try:
                        # Check if we must remove access for that project
                        if project['project_role'] == '':
                            # No more access to that project for that user group - remove all access!
                            TeraServiceAccess.delete_service_access_for_user_group_for_project(
                                id_user_group=json_user_group['id_user_group'], id_project=int(project['id_project']))
                            continue

                        # Find id_service_role
                        project_service_role = \
                            TeraServiceRole.get_specific_service_role_for_project(service_id=Globals.opentera_service_id,
                                                                                  project_id=int(project['id_project']),
                                                                                  rolename=project['project_role'])
                        TeraServiceAccess.update_service_access_for_user_group_for_project(
                            id_service=Globals.opentera_service_id, id_user_group=json_user_group['id_user_group'],
                            id_service_role=project_service_role.id_service_role, id_project=int(project['id_project']))

                    except exc.SQLAlchemyError:
                        import sys
                        print(sys.exc_info())
                        return '', 500

        update_user_group = TeraUserGroup.get_user_group_by_id(json_user_group['id_user_group'])

        return [update_user_group.to_json()]

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific user group',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete user group (only a site admin that includes that user group in '
                             'their site can delete)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # Only site admin with an user group that includes that site can delete
        user_group = TeraUserGroup.get_user_group_by_id(id_todel)
        if not set(user_access.get_accessible_sites(admin_only=True)).intersection(user_group.get_sites_roles().keys()):
            return '', 403

        # If we are here, we are allowed to delete that user group. Do so.
        try:
            TeraUserGroup.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200

