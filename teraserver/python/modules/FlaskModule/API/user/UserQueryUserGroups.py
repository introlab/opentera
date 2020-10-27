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
post_schema = api.schema_model('user_group', {'properties': TeraUserGroup.get_json_schema(),
                                                   'type': 'object',
                                                   'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='User group ID to delete', required=True)


class UserQueryUserGroups(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @staticmethod
    def get_projects_roles_json(user_access, user_group_id: int):
        projects_list = []
        access = user_access.query_project_access_for_user_group(user_group_id=user_group_id,
                                                                 admin_only=False,
                                                                 include_projects_without_access=
                                                                 False
                                                                 )
        for project, project_role in access.items():
            # Remove site information for projects
            proj_access_json = project.to_json(ignore_fields=['id_site', 'site_name'])
            if project_role:
                proj_access_json['project_access_role'] = project_role['project_role']
                if project_role['inherited']:
                    proj_access_json['project_access_inherited'] = True
            projects_list.append(proj_access_json)

        return projects_list

    @staticmethod
    def get_sites_roles_json(user_access, user_group_id: int):
        sites_list = []
        access = user_access.query_site_access_for_user_group(user_group_id=user_group_id,
                                                              admin_only=False,
                                                              include_sites_without_access=False)
        for site, site_role in access.items():
            site_access_json = site.to_json()
            if site_role:
                site_access_json['site_access_role'] = site_role['site_role']
                if site_role['inherited']:
                    site_access_json['site_access_inherited'] = True
            else:
                site_access_json['site_access_role'] = None
            sites_list.append(site_access_json)
        return sites_list

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
                user_groups = user_access.query_usergroups_for_user(args['id_user'])
        else:
            # If we have no arguments, return all accessible user groups
            user_groups = user_access.get_accessible_users_groups()

        if user_groups:
            user_groups_list = []
            for group in user_groups:
                if group is not None:
                    group_json = group.to_json(minimal=args['list'])

                    if not args['list']:
                        # Sites for that user group
                        sites_list = UserQueryUserGroups.get_sites_roles_json(user_access=user_access,
                                                                              user_group_id=group.id_user_group)
                        group_json['user_group_sites_access'] = sites_list

                        # Projects for that user group
                        projects_list = UserQueryUserGroups.get_projects_roles_json(user_access=user_access,
                                                                                    user_group_id=group.id_user_group)

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
            return gettext('Missing id_user_group'), 400

        # Check if current user has at least an accessible site as admin
        current_user_sites = user_access.get_accessible_sites(admin_only=True)
        if not current_user_sites:
            return gettext('Forbidden'), 403

        # Check if we have site access to handle separately
        json_sites = None
        if 'user_group_sites_access' in json_user_group:
            json_sites = json_user_group.pop('user_group_sites_access')
            # Check if the current user is site admin in all of those sites
            site_ids = [site['id_site'] for site in json_sites]

            for site_id in site_ids:
                if user_access.get_site_role(site_id) != 'admin':
                    return gettext('No site admin access for at a least one site in the list'), 403

        # If user is not super admin, we must add site access to at least one of the current user's site where he is
        # admin to allow further modification on user groups
        # if not json_sites and not current_user.user_superadmin:
        #     site = {'id_site': current_user_sites[0].id_site, 'site_access_role': 'user'}
        #     json_sites = [site]

        # Check if we have project access to handle separately
        json_projects = None
        if 'user_group_projects_access' in json_user_group:
            json_projects = json_user_group.pop('user_group_projects_access')
            # Check if the current user is site admin in all of those projects
            project_ids = [project['id_project'] for project in json_projects]

            from libtera.db.models.TeraProject import TeraProject
            for proj_id in project_ids:
                proj = TeraProject.get_project_by_id(proj_id)
                if proj and user_access.get_site_role(proj.id_site) != 'admin':
                    return gettext('No site admin access for at a least one project in the list'), 403

        # Do the update!
        if json_user_group['id_user_group'] > 0:
            # Already existing user group
            try:
                TeraUserGroup.update(json_user_group['id_user_group'], json_user_group)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryUserGroups.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # Creates a new user group
            try:
                new_user_group = TeraUserGroup()
                new_user_group.from_json(json_user_group)
                TeraUserGroup.insert(new_user_group)
                # Update ID User Group for further use
                json_user_group['id_user_group'] = new_user_group.id_user_group
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryUserGroups.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        update_user_group = TeraUserGroup.get_user_group_by_id(json_user_group['id_user_group'])
        json_user_group = update_user_group.to_json()
        if json_sites:
            for site in json_sites:
                try:
                    # Check if we must remove access for that site
                    if 'site_access_role' not in site or site['site_access_role'] == '':
                        # No more access to that site for that user group - remove all access!
                        TeraServiceAccess.delete_service_access_for_user_group_for_site(
                            id_user_group=json_user_group['id_user_group'], id_site=int(site['id_site']))
                        continue

                    # Find id_service_role
                    site_service_role = \
                        TeraServiceRole.get_specific_service_role_for_site(service_id=Globals.opentera_service_id,
                                                                           site_id=int(site['id_site']),
                                                                           rolename=site['site_access_role'])
                    TeraServiceAccess.update_service_access_for_user_group_for_site(
                        id_service=Globals.opentera_service_id, id_user_group=json_user_group['id_user_group'],
                        id_service_role=site_service_role.id_service_role, id_site=int(site['id_site']))
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryUserGroups.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        if json_projects:
            for project in json_projects:
                try:
                    # Check if we must remove access for that project
                    if 'project_access_role' not in project or project['project_access_role'] == '':
                        # No more access to that project for that user group - remove all access!
                        TeraServiceAccess.delete_service_access_for_user_group_for_project(
                            id_user_group=json_user_group['id_user_group'], id_project=int(project['id_project']))
                        continue

                    # Find id_service_role
                    project_service_role = \
                        TeraServiceRole.get_specific_service_role_for_project(service_id=Globals.opentera_service_id,
                                                                              project_id=int(project['id_project']),
                                                                              rolename=project['project_access_role'])
                    TeraServiceAccess.update_service_access_for_user_group_for_project(
                        id_service=Globals.opentera_service_id, id_user_group=json_user_group['id_user_group'],
                        id_service_role=project_service_role.id_service_role, id_project=int(project['id_project']))

                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryUserGroups.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500
            # Returns full list in reply
            json_user_group['user_group_projects_access'] = UserQueryUserGroups.get_projects_roles_json(
                user_access=user_access, user_group_id=json_user_group['id_user_group'])

        if json_sites:
            # Returns full list in reply - done here, since inheritance might occurs if done before project completed
            json_user_group['user_group_sites_access'] = UserQueryUserGroups.get_sites_roles_json(
                user_access=user_access, user_group_id=json_user_group['id_user_group'])
        return [json_user_group]

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
        accessible_sites = user_access.get_accessible_sites(admin_only=True)
        sites_roles = user_group.get_sites_roles().keys()  # When there's no role, only super admin can delete!
        if not set(accessible_sites).intersection(sites_roles) and not current_user.user_superadmin:
            return '', 403

        # If we are here, we are allowed to delete that user group. Do so.
        try:
            TeraUserGroup.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting:
            # - Associated users with that user group
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryUserGroups.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Can\'t delete user group: please delete all users part of that user group before deleting.'
                           ), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryUserGroups.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200

