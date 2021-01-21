from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from sqlalchemy import exc
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraUserGroup import TeraUserGroup
from flask_babel import gettext
from modules.DatabaseModule.DBManager import DBManager
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user', type=int, help='ID of the user to query')
get_parser.add_argument('id_user_group', type=int, help='ID of the user group to get all users from')
get_parser.add_argument('id_project', type=int, help='ID of the project to get all users that has access to it')
get_parser.add_argument('user_uuid', type=str, help='User UUID to query')
get_parser.add_argument('uuid', type=str, help='Alias for "user_uuid"')
get_parser.add_argument('username', type=str, help='Username of the user to query')
get_parser.add_argument('self', type=inputs.boolean, help='Query information about the currently logged user')
get_parser.add_argument('enabled', type=inputs.boolean, help='Only returns users with the specified enabled status')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ID, name, enabled)')
get_parser.add_argument('with_usergroups', type=inputs.boolean, help='Include usergroups information for each user.')
get_parser.add_argument('with_status', type=inputs.boolean, help='Include status information - offline, online, busy '
                                                                 'for each user')

post_parser = reqparse.RequestParser()
# post_parser.add_argument('user', type=str, location='json', help='User to create / update. If structure has a field '
#                                                                '"user_groups", also update user groups for that user',
#                          required=True)

post_schema = api.schema_model('user_user', {'properties': TeraUser.get_json_schema(), 'type': 'object',
                                             'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='User ID to delete', required=True)


class UserQueryUsers(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get user information. If no id specified, returns all accessible users',
             responses={200: 'Success',
                        500: 'Database error'})
    def get(self):
        parser = get_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        args = parser.parse_args()

        user_access = DBManager.userAccess(current_user)

        users = []

        if args['uuid']:
            args['user_uuid'] = args['uuid']

        # If we have a user_uuid, query for that user if accessible
        if args['user_uuid']:
            if args['user_uuid'] in user_access.get_accessible_users_uuids():
                users.append(TeraUser.get_user_by_uuid(args['user_uuid']))
        elif args['id_user']:
            if args['id_user'] in user_access.get_accessible_users_ids():
                users.append(current_user.get_user_by_id(args['id_user']))
        elif args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                users = user_access.query_users_for_project(project_id=args['id_project'], enabled_only=True,
                                                            include_super_admins=True)
        elif args['self'] is not None:
            users.append(current_user)
        elif args['username'] is not None:
            user = TeraUser.get_user_by_username(args['username'])
            if user is not None and user.id_user in user_access.get_accessible_users_ids():
                users.append(user)
        elif args['id_user_group']:
            if args['id_user_group'] in user_access.get_accessible_users_groups_ids():
                users = user_access.query_users_for_usergroup(args['id_user_group'])
        else:
            # If we have no arguments, return all accessible users
            users = user_access.get_accessible_users()

        if users:
            users_list = []
            online_users = []
            busy_users = []
            if args['with_status']:
                # Query users status
                rpc = RedisRPCClient(self.module.config.redis_config)
                online_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_users')
                busy_users = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'busy_users')

            for user in users:
                if user is not None:
                    # Filter not enabled users
                    if args['enabled'] is not None:
                        if user.user_enabled != args['enabled']:
                            continue

                    user_json = user.to_json(minimal=args['list'])
                    if args['list'] is None:
                        # If user is "self", append projects and sites roles
                        if user.id_user == current_user.id_user:
                            # Sites
                            sites = user_access.get_accessible_sites()
                            sites_list = []
                            for site in sites:
                                site_json = site.to_json()
                                site_json['site_role'] = user_access.get_site_role(site.id_site)
                                sites_list.append(site_json)
                            user_json['sites'] = sites_list

                            # Projects
                            projects = user_access.get_accessible_projects()
                            proj_list = []
                            for project in projects:
                                proj_json = project.to_json()
                                proj_json['project_role'] = \
                                    user_access.get_project_role(project.id_project)
                                proj_list.append(proj_json)
                            user_json['projects'] = proj_list

                    if args['with_usergroups']:
                        # Append user groups
                        user_groups_list = []
                        for user_group in user_access.query_usergroups_for_user(user.id_user):
                            user_groups_list.append(user_group.to_json(minimal=True))
                        user_json['user_user_groups'] = user_groups_list

                    if args['with_status']:
                        user_json['user_busy'] = user.user_uuid in busy_users
                        user_json['user_online'] = user.user_uuid in online_users

                    users_list.append(user_json)
            return jsonify(users_list)

        return [], 200
        # try:
        #     users = TeraUser.query_data(my_args)
        #     users_list = []
        #     for user in users:
        #         users_list.append(user.to_json())
        #     return jsonify(users_list)
        # except InvalidRequestError:
        #     return '', 500

    @user_multi_auth.login_required
    # @api.expect(post_parser)
    @api.expect(post_schema)
    @api.doc(description='Create / update user. id_user must be set to "0" to create a new user. User can be modified '
                         'if: current user is super admin or user is part of a project which the current user is admin.'
                         ' Promoting a user to super admin is restricted to super admins.'
                         '"If data contains "user_user_groups, also set user groups for that user.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified user',
                        400: 'Badly formed JSON or missing field(id_user or missing password when new user) in the '
                             'JSON body',
                        409: 'Username is already taken',
                        500: 'Internal error when saving user'})
    def post(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])

        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_user = request.json['user']

        # Validate if we have an id_user
        if 'id_user' not in json_user:
            return gettext('Missing id_user'), 400

        # Manage user groups
        user_user_groups_ids = []
        update_user_groups = False
        if 'user_user_groups' in json_user:
            current_user_groups = user_access.get_accessible_users_groups_ids(admin_only=True)
            # if json_user['id_user'] > 0:
            #     return gettext('User groups may be specified with that API only on a new user. Use '
            #                    '"user_usergroups" instead'), 400
            user_user_groups = json_user.pop('user_user_groups')
            # Check if the current user can modify each of the user groups
            user_user_groups_ids = [group['id_user_group'] for group in user_user_groups]
            for user_group_id in user_user_groups_ids:
                if user_group_id not in current_user_groups:
                    return gettext('No access for at a least one user group in the list'), 403
            update_user_groups = True

        # Check if current user can modify the posted user
        if json_user['id_user'] > 0:
            if json_user['id_user'] != current_user.id_user:
                # Existing user and not ourselves
                update_user = TeraUser.get_user_by_id(json_user['id_user'])
                if not update_user:
                    return '', 400
                if not current_user.user_superadmin:
                    site_roles = update_user.get_sites_roles()
                    user_sites_ids = [site.id_site for site in site_roles]
                    # if json_user['id_user'] not in user_access.get_accessible_users_ids(admin_only=True):
                    if len(set(user_sites_ids).intersection(user_access.get_accessible_sites_ids(admin_only=True))) == 0:
                        return gettext('Forbidden'), 403
        else:
            # New user can be created by superadmins and by site admins, when user groups are specified
            # If update_user_group is set, we have new user groups with that user, and we are admin in all of them!
            if not current_user.user_superadmin and not update_user_groups:
                return gettext('Forbidden'), 403

        # Only superadmin can modify superadmin status
        if not current_user.user_superadmin and 'user_superadmin' in json_user:
            json_user['user_superadmin'] = False

        # Do the update for user
        new_user = None
        if json_user['id_user'] > 0:
            if 'user_username' in json_user:
                return gettext('Username can\'t be modified'), 400

            # Already existing user
            try:
                TeraUser.update(json_user['id_user'], json_user)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryUsers.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New user, check if password is set
            # if 'user_password' not in json_user:
            #     return gettext('Password required'), 400

            # Validate required fields
            missing_fields = TeraUser.validate_required_fields(json_data=json_user, ignore_fields=['user_uuid',
                                                                                                   'user_superadmin'])
            if missing_fields:
                return gettext('Missing required fields: ') + str(missing_fields), 400

            if json_user['user_password'] is None or json_user['user_password'] == '':
                return gettext('Invalid password'), 400

            # Check if username is already taken
            if TeraUser.get_user_by_username(json_user['user_username']) is not None:
                return gettext('Username unavailable.'), 409

            # Ok so far, we can try to create the user!
            try:
                new_user = TeraUser()
                new_user.from_json(json_user)
                TeraUser.insert(new_user)
                # Update ID User for further use
                json_user['id_user'] = new_user.id_user
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryUsers.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        update_user = TeraUser.get_user_by_id(json_user['id_user'])

        # Update user groups, if needed
        if update_user_groups:
            if not update_user.user_superadmin:  # Don't add groups if super admin!
                if new_user:
                    # New user - directly update the list
                    update_user.user_user_groups = [TeraUserGroup.get_user_group_by_id(user_group_id)
                                                    for user_group_id in user_user_groups_ids]
                    update_user.commit()
                else:
                    # Updated user - first, we add groups not already there
                    update_user_current_groups = [group.id_user_group for group in update_user.user_user_groups]
                    user_groups_to_add = set(user_user_groups_ids).difference(update_user_current_groups)
                    update_user.user_user_groups.extend([TeraUserGroup.get_user_group_by_id(user_group_id)
                                                         for user_group_id in user_groups_to_add])

                    # Then, we delete groups that the current user has access, but are not present in the posted list,
                    # without touching groups already there
                    current_user_groups = user_access.get_accessible_users_groups_ids(admin_only=True)
                    update_user_current_groups.extend(list(user_groups_to_add))
                    missing_user_groups = set(current_user_groups).difference(user_user_groups_ids)
                    for user_group_id in missing_user_groups:
                        if user_group_id in update_user_current_groups:
                            update_user.user_user_groups.remove(TeraUserGroup.get_user_group_by_id(user_group_id))

                    update_user.commit()

            # Check if there's some user groups for the updated user that we need to delete
            # id_groups_to_delete = set([group.id_user_group for group in update_user.user_user_groups])\
            #     .difference(user_user_groups_ids)
            #
            # for id_to_del in id_groups_to_delete:
            #     uug_to_del = TeraUserUserGroup.query_user_user_group_for_user_user_group(user_id=update_user.id_user,
            #                                                                              user_group_id=id_to_del)
            #     TeraUserUserGroup.delete(id_todel=uug_to_del.id_user_user_group)
            #
            # # Update / insert user groups
            # for user_group in user_user_groups:
            #     if not TeraUserUserGroup.query_user_user_group_for_user_user_group(user_id=update_user.id_user,
            #                                                                        user_group_id=
            #                                                                        user_group['id_user_group']):
            #         # Group not already associated - associates!
            #         TeraUserUserGroup.insert_user_user_group(id_user_group=user_group['id_user_group'],
            #                                                  id_user=update_user.id_user)

        return [update_user.to_json()]

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific user',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete user (only super admin can delete)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if we are trying to delete ourselves!
        if id_todel == current_user.id_user:
            return gettext('Sorry, you can\'t delete yourself!'), 403

        # Check if current user can delete
        full_delete = current_user.user_superadmin
        dif_groups = []
        user_to_del = TeraUser.get_user_by_id(id_todel)
        if not user_to_del:
            return gettext('Invalid id'), 400
        if not current_user.user_superadmin:
            # We must check if we need to remove usergroups from that user or delete it completely
            access_user_groups = user_access.get_accessible_users_groups(admin_only=True, by_sites=True)
            if not access_user_groups:
                return gettext('Forbidden'), 403
            dif_groups = set(user_to_del.user_user_groups).difference(access_user_groups)
            if len(dif_groups) == 0:
                full_delete = True

        if full_delete:
            # If we are here, we are allowed to delete that user. Do so.
            try:
                TeraUser.delete(id_todel=id_todel)
            except exc.IntegrityError as e:
                # Causes that could make an integrity error when deleting:
                # - Associated sessions in which the user is part of
                # - Sessions that the user created
                # - Assets that the user created
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryUsers.__name__,
                                             'delete', 500, 'Database error', str(e))
                if 't_sessions_users' in str(e.args):
                    return gettext('Can\'t delete user: please remove all sessions that this user is part of before '
                                   'deleting.'), 500
                if 't_sessions_id_creator' in str(e.args):
                    return gettext('Can\'t delete user: please remove all sessions created by this user before '
                                   'deleting.'), 500
                return gettext('Can\'t delete user: please delete all assets created by this user before deleting.')\
                    , 500
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryUsers.__name__,
                                             'delete', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # Only remove usergroups from that user so that user is "apparently" deleted to the site admin
            user_groups = user_to_del.user_user_groups
            for user_group in user_groups:
                if user_group.id_user_group not in dif_groups:
                    user_to_del.user_user_groups.remove(user_group)
            user_to_del.commit()

        return '', 200

