from flask import request
from flask_restx import Resource, reqparse
from sqlalchemy import exc
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.LoginModule.LoginModule import LoginModule, current_service
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraServiceRole import TeraServiceRole
from opentera.db.models.TeraUserGroup import TeraUserGroup
from flask_babel import gettext
from modules.DatabaseModule.DBManager import DBManager, DBManagerTeraServiceAccess

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user_group', type=int, help='ID of the user group to query')
get_parser.add_argument('id_project', type=int, help='ID of the project to query user group with access to')
get_parser.add_argument('id_site', type=int, help='ID of the site to query user group with access to')

post_parser = api.parser()
post_schema = api.schema_model('service_user_group', {'properties': TeraUserGroup.get_json_schema(), 'type': 'object',
                                                      'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='User group ID to delete', required=True)


class ServiceQueryUserGroups(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get user group information. If no id specified, returns all accessible users groups',
             responses={200: 'Success',
                        500: 'Database error'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        """
        Get usergroups
        """
        service_access: DBManagerTeraServiceAccess = DBManager.serviceAccess(current_service)
        args = get_parser.parse_args()
        user_groups = []

        if args['id_user_group']:
            if args['id_user_group'] in service_access.get_accessible_usergroups_ids():
                user_groups.append(TeraUserGroup.get_user_group_by_id(args['id_user_group']))
        elif args['id_project']:
            if args['id_project'] not in service_access.get_accessible_projects_ids():
                return gettext('Forbidden'), 403
            user_groups = service_access.query_usergroups_for_project(args['id_project'])
        elif args['id_site']:
            if args['id_site'] not in service_access.get_accessibles_sites_ids():
                return gettext('Forbidden'), 403
            user_groups = service_access.query_usergroups_for_site(args['id_site'])
        else:
            # If we have no arguments, return all accessible user groups
            user_groups = service_access.get_accessible_usergroups()

        user_groups_list = []
        if user_groups:
            for group in user_groups:
                if group is not None:
                    group_json = group.to_json()
                    user_groups_list.append(group_json)
        return user_groups_list

    @api.doc(description='Create / update user group. id_user_group must be set to "0" to create a new user group. User'
                         ' groups can be modified if the service can access it (user group has a service role).',
             responses={200: 'Success',
                        403: 'Logged service can\'t create/update the specified user group',
                        400: 'Badly formed JSON or missing field(id_user_group) in the JSON body',
                        500: 'Internal error when saving user group'},
             params={'token': 'Access token'})
    @api.expect(post_schema)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        """
        Create / update usergroup
        """
        service_access: DBManagerTeraServiceAccess = DBManager.serviceAccess(current_service)

        if 'user_group' not in request.json:
            return gettext('Missing user_group'), 400

        # Using request.json instead of parser, since parser messes up the json!
        json_user_group = request.json['user_group']

        # Validate if we have an id_user_group
        if 'id_user_group' not in json_user_group:
            return gettext('Missing id_user_group'), 400

        # Check if we have service access to handle
        json_access = None
        if 'user_group_services_access' in json_user_group:
            json_access = json_user_group.pop('user_group_services_access')
            accessible_projects_ids = service_access.get_accessible_projects_ids()
            accessible_sites_ids = service_access.get_accessibles_sites_ids()

            # Check if access only are for the current service
            for access in json_access:
                if 'service_role_name' not in access and 'id_service_role' not in access:
                    return gettext('Missing service role name or id_service_role'), 400

                if 'id_service_role' in access:
                    # Fill the "missing" informations from that role
                    role: TeraServiceRole = TeraServiceRole.get_service_role_by_id(access['id_service_role'])
                    if not role:
                        return gettext('Forbidden'), 403
                    access['id_site'] = role.id_site
                    access['id_project'] = role.id_project
                    access['id_service'] = role.id_service

                # Service check
                if 'id_service' in access and access['id_service'] != current_service.id_service:
                    return gettext('Can\'t set access to service other than self'), 403
                if 'id_service' not in access:
                    access['id_service'] = current_service.id_service

                # Project check
                if 'id_project' in access and access['id_project'] not in accessible_projects_ids:
                    return gettext('No access for at a least one project in the list'), 403
                if 'id_project' not in access:
                    access['id_project'] = None

                # Site check
                if 'id_site' in access and access['id_site'] not in accessible_sites_ids:
                    return gettext('No access for at a least one site in the list'), 403
                if 'id_site' not in access:
                    access['id_site'] = None

                # Service role check
                if 'service_role_name' in access:
                    # Find the related id_service role
                    role = TeraServiceRole.get_service_role_by_name(service_id=current_service.id_service,
                                                                    rolename=access['service_role_name'],
                                                                    site_id=access['id_site'],
                                                                    project_id=access['id_project'])
                    if not role:
                        return gettext('Bad role name for service'), 400
                    access['id_service_role'] = role.id_service_role

        # Do the update!
        if json_user_group['id_user_group'] > 0:
            # Already existing user group
            try:
                TeraUserGroup.update(json_user_group['id_user_group'], json_user_group)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryUserGroups.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # Creates a new user group
            if not json_access:
                return gettext('A new usergroup must have at least one service access'), 400
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
                                             ServiceQueryUserGroups.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        update_user_group = TeraUserGroup.get_user_group_by_id(json_user_group['id_user_group'])
        json_user_group = update_user_group.to_json()
        if json_access:
            current_access = TeraServiceAccess.get_service_access_for_user_group(
                id_user_group=json_user_group['id_user_group'],
                id_service=current_service.id_service
            )
            for access in current_access:
                # Check if access is in the current access list
                found_access = [acc for acc in json_access if acc['id_service_role'] == access.id_service_role]
                if not found_access:
                    TeraServiceAccess.delete(access.id_service_access)

            # Add new access
            for access in json_access:
                TeraServiceAccess.update_service_access_for_user_group(id_service=current_service.id_service,
                                                                       id_user_group=json_user_group['id_user_group'],
                                                                       id_service_role=access['id_service_role'],
                                                                       id_project=access['id_project'],
                                                                       id_site=access['id_site'])
        return json_user_group

    @api.doc(description='Delete a specific user group',
             responses={200: 'Success',
                        403: 'Service can\'t delete user group (no access to it)',
                        500: 'Database error.'},
             params={'token': 'Access token'})
    @api.expect(delete_parser)
    @LoginModule.service_token_or_certificate_required
    def delete(self):
        """
        Delete a specific usergroup
        """
        service_access: DBManagerTeraServiceAccess = DBManager.serviceAccess(current_service)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current service can delete
        # Only site admin with an user group that includes that site can delete
        if id_todel not in service_access.get_accessible_usergroups_ids():
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete that user group. Do so.
        try:
            TeraUserGroup.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting:
            # - Associated users with that user group
            self.module.logger.log_warning(self.module.module_name, ServiceQueryUserGroups.__name__, 'delete', 500,
                                           'Integrity error', str(e))
            return gettext('Can\'t delete user group: please delete all users part of that user group before deleting.'
                           ), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryUserGroups.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200

