from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from sqlalchemy import exc
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraServiceRole import TeraServiceRole
from modules.DatabaseModule.DBManager import DBManager
import modules.Globals as Globals

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user', type=int, help='ID of the user from which to request all site roles')
get_parser.add_argument('id_user_group', type=int, help='ID of the user group from which to request all site roles')
get_parser.add_argument('id_site', type=int, help='ID of the site from which to request all user groups roles')
get_parser.add_argument('admins', type=inputs.boolean, help='Flag to limit to sites from which the user group is an '
                                                            'admin or users in site that have the admin role')
get_parser.add_argument('by_users', type=inputs.boolean, help='If specified, returns roles by users instead of by user'
                                                              'groups')
get_parser.add_argument('with_usergroups', type=inputs.boolean, help='Used With the "by_users" parameter, it instead '
                                                                     'returns the usergroups of each user.')
get_parser.add_argument('with_empty', type=inputs.boolean, help='Used with id_site, also return user or user groups '
                                                                'that don\'t have any access to the site. Used with '
                                                                'id_user_group, also return sites that don\'t '
                                                                'have any access with that user group')

# post_parser = reqparse.RequestParser()
post_schema = api.schema_model('user_site_access', {
    'properties': {
        'site_access': {
            'properties': {
                'id_site': {
                    'type': 'integer',
                    'required': True
                },
                'id_user_group': {
                    'type': 'integer',
                    'required': True
                },
                'site_access_role': {
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
delete_parser.add_argument('id', type=int, help='Site Access ID to delete', required=True)


class UserQuerySiteAccess(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get user roles for sites. Only one  parameter required and supported at once.',
             responses={200: 'Success - returns list of users roles in sites',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error occured when loading sites roles'})
    def get(self):
        from opentera.db.models.TeraSite import TeraSite
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
                access = user_access.query_site_access_for_user(user_id=user_id, admin_only=args['admins'] is not None)

        # Query access for user group
        if args['id_user_group']:
            if args['id_user_group'] in user_access.get_accessible_users_groups_ids():
                access = user_access.query_site_access_for_user_group(user_group_id=args['id_user_group'],
                                                                      admin_only=args['admins'] is not None,
                                                                      include_sites_without_access=args['with_empty'])

        # Query access for site id
        if args['id_site']:
            site_id = args['id_site']
            access = user_access.query_access_for_site(site_id=site_id, admin_only=args['admins'] is not None,
                                                       include_empty_groups=args['with_empty'])

        if access is not None:
            access_list = []
            if not args['by_users'] or args['id_user']:
                for site, site_role in access.items():
                    site_access_json = site.to_json()
                    if site_role:
                        site_access_json['site_access_role'] = site_role['site_role']
                        if site_role['inherited']:
                            site_access_json['site_access_inherited'] = True
                    else:
                        site_access_json['site_access_role'] = None

                    access_list.append(site_access_json)
            else:
                users_list = []
                sites_list = []
                if args['id_site']:
                    for usergroup, site_role in access.items():
                        users_list.extend(user_access.query_users_for_usergroup(user_group_id=usergroup.id_user_group))
                    sites_list = [TeraSite.get_site_by_id(args['id_site'])]

                if args['id_user_group']:
                    users_list = user_access.query_users_for_usergroup(user_group_id=args['id_user_group'])
                    sites_list = [site for site in access]

                user_ids = []
                for user in users_list:
                    if user.id_user in user_ids:
                        continue  # Don't add duplicates users
                    user_ids.append(user.id_user)
                    for site in sites_list:
                        site_role = user_access.get_user_site_role(user_id=user.id_user, site_id=site.id_site)
                        if args['admins'] and site_role and site_role['site_role'] != 'admin':
                            site_role = None
                        site_access_json = {'id_user': user.id_user,
                                            'id_site': site.id_site,
                                            'user_name': user.get_fullname(),
                                            'user_enabled': user.user_enabled,
                                            'site_access_role': site_role['site_role'] if site_role else None,
                                            'site_access_inherited': site_role['inherited'] if site_role else None
                                            }
                        if site_access_json:
                            if args['with_usergroups']:
                                usergroups = user_access.query_usergroups_for_user(user.id_user)
                                ug_list = [ug.to_json() for ug in usergroups]
                                site_access_json['user_groups'] = ug_list

                            access_list.append(site_access_json)
            return access_list

        # No access, but still fine
        return [], 200

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create/update site access for a user group.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify this site or user access (site admin access required)',
                        400: 'Badly formed JSON or missing fields(id_user or id_site) in the JSON body',
                        500: 'Database error'})
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_sites = request.json['site_access']

        if not isinstance(json_sites, list):
            json_sites = [json_sites]

        # Validate if we have everything needed
        json_rval = []
        for json_site in json_sites:
            if 'id_user_group' not in json_site:
                return gettext('Missing id_user_group'), 400
            if 'id_site' not in json_site:
                return gettext('Missing id_site'), 400
            if 'site_access_role' not in json_site and 'id_service_role' not in json_site:
                return gettext('Missing role name or id'), 400

            # Check if current user can change the access for that site
            if user_access.get_site_role(site_id=json_site['id_site']) != 'admin':
                return gettext('Forbidden'), 403

            site_service_role = None
            if 'site_access_role' in json_site:
                # Check if we must remove access for that site
                if json_site['site_access_role'] == '':
                    # No more access to that site for that user group - remove all access!
                    TeraServiceAccess.delete_service_access_for_user_group_for_site(
                        id_user_group=json_site['id_user_group'], id_site=json_site['id_site'])
                    continue

                # If we are setting a "user" role for a site, check if there's already such an inherited role from
                # projects
                if json_site['site_access_role'] == 'user':
                    from opentera.db.models.TeraUserGroup import TeraUserGroup
                    user_group = TeraUserGroup.get_user_group_by_id(json_site['id_user_group'])
                    projects_roles = [role for project, role in user_group.get_projects_roles(no_inheritance=True)
                                      .items() if project.id_site == json_site['id_site']]
                    if projects_roles:
                        # Delete that site access without adding new access
                        TeraServiceAccess.delete_service_access_for_user_group_for_site(
                            id_user_group=json_site['id_user_group'], id_site=json_site['id_site'])
                        continue

                # Find id_service_role for that
                site_service_role = \
                    TeraServiceRole.get_specific_service_role_for_site(service_id=Globals.opentera_service_id,
                                                                       site_id=json_site['id_site'],
                                                                       rolename=json_site['site_access_role'])
            if 'id_service_role' in json_site:
                if json_site['id_service_role'] == 0:
                    # No more access to that site for that user group - remove all access!
                    TeraServiceAccess.delete_service_access_for_user_group_for_site(
                        id_user_group=json_site['id_user_group'], id_site=json_site['id_site'])
                    continue
                site_service_role = TeraServiceRole.get_service_role_by_id(json_site['id_service_role'])

            if not site_service_role:
                return gettext('Invalid role name or id for that site'), 400

            # Do the update!
            try:
                # access = TeraSiteAccess.update_site_access(json_site['id_user_group'], json_site['id_site'],
                #                                            json_site['site_access_role'])
                access = TeraServiceAccess.update_service_access_for_user_group_for_site(
                    id_service=Globals.opentera_service_id, id_user_group=json_site['id_user_group'],
                    id_service_role=site_service_role.id_service_role, id_site=json_site['id_site'])

            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQuerySiteAccess.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

            if access:
                json_access = access.to_json()
                # For backwards compatibility with "old" API
                json_access['id_site_access'] = access.id_service_access
                json_access['site_access_role'] = access.service_access_role.service_role_name
                json_rval.append(json_access)

        return json_rval

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific site access',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete site access(only user who is admin in that site can remove it)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        site_access = TeraServiceAccess.get_service_access_by_id(id_todel)
        if not site_access:
            return gettext('No site access to delete'), 400

        # Check if current user can delete
        if user_access.get_site_role(site_access.service_access_role.id_site) != 'admin':
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceAccess.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySiteAccess.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200

