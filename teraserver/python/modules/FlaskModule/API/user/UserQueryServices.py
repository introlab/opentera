from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs

from libtera.db.models import TeraServiceProject
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraService import TeraService
from libtera.db.models.TeraServiceRole import TeraServiceRole
from modules.DatabaseModule.DBManager import DBManager
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_service', type=int, help='ID of the service to query')
get_parser.add_argument('id_project', type=int, help='ID of the project to query services from')
get_parser.add_argument('id', type=int, help='Alias for "id_service"')
get_parser.add_argument('uuid', type=str, help='Service UUID to query')
get_parser.add_argument('key', type=str, help='Service Key to query')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')
get_parser.add_argument('with_config', type=inputs.boolean, help='Only return services with editable configuration')
get_parser.add_argument('with_projects', type=inputs.boolean, help='Return services with service projects')


# post_parser = reqparse.RequestParser()
# post_parser.add_argument('service', type=str, location='json', help='Service to create / update', required=True)
post_schema = api.schema_model('user_service', {'properties': TeraService.get_json_schema(),
                                                'type': 'object',
                                                'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Service ID to delete', required=True)


class UserQueryServices(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get services information. Only one of the ID parameter is supported and required at once.',
             responses={200: 'Success - returns list of services',
                        500: 'Database error'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

        services = []
        # If we have no arguments, return all accessible projects
        # queried_user = current_user

        if args['id']:
            args['id_service'] = args['id']

        if args['id_service']:
            if args['id_service'] in user_access.get_accessible_services_ids():
                services = [TeraService.get_service_by_id(args['id_service'])]
        elif args['uuid']:
            # If we have a service uuid, ensure that service is accessible
            service = TeraService.get_service_by_uuid(args['uuid'])
            if service and service.id_service in user_access.get_accessible_services_ids():
                services = [service]
        elif args['key']:
            service = TeraService.get_service_by_key(args['key'])
            if service and service.id_service in user_access.get_accessible_services_ids():
                services = [service]
        elif args['id_project']:
            services = user_access.query_services_for_project(args['id_project'])
        else:
            # No arguments - return all acceessible services
            services = user_access.get_accessible_services(include_system_services=args['with_config'])

        try:
            services_list = []

            for service in services:
                if args['with_config']:
                    if not service.service_editable_config:
                        continue
                if args['with_projects']:
                    # Get all current association for service
                    current_projects = TeraServiceProject.get_projects_for_service(id_service=service.id_service)
                    service_projects = []
                    for project in current_projects:
                        service_projects.append(project.to_json())
                service_json = service.to_json(minimal=args['list'])
                services_list.append(service_json)

            return jsonify(services_list)

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryServices.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create / update services. id_service must be set to "0" to create a new '
                         'service. A service can be created/modified only by super-admins. If data contains "roles", '
                         'also update the roles with the list.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified service',
                        400: 'Badly formed JSON or missing fields(id_service) in the JSON body',
                        500: 'Internal error occured when saving service'})
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        # Check if user is a super admin
        if not current_user.user_superadmin:
            return gettext('Forbidden'), 403

        # Using request.json instead of parser, since parser messes up the json!
        json_service = request.json['service']

        # Validate if we have an id
        if 'id_service' not in json_service:
            return gettext('Missing id_service'), 400

        # Check if that service is in the accessible service list, even for super admins since system services are not
        # modifiables
        if json_service['id_service'] not in user_access.get_accessible_services_ids() \
                and json_service['id_service'] != 0:
            return gettext('Forbidden'), 403

        # Manage service roles
        service_roles = []
        if 'roles' in json_service:
            service_roles = json_service.pop('roles')

        # Do the update!
        import jsonschema
        if json_service['id_service'] > 0:
            # Already existing
            try:
                if 'service_system' in json_service:
                    service = TeraService.get_service_by_id(json_service['id_service'])
                    if service.service_system != json_service['service_system']:
                        return gettext('Can\'t change system services from that API'), 403
                TeraService.update(json_service['id_service'], json_service)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryServices.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
            except jsonschema.exceptions.SchemaError:
                return gettext('Invalid config json schema'), 400
        else:
            # New
            try:
                new_service = TeraService()
                new_service.from_json(json_service)
                TeraService.insert(new_service)
                # Update ID for further use
                json_service['id_service'] = new_service.id_service
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryServices.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
            except jsonschema.exceptions.SchemaError:
                return gettext('Invalid config json schema'), 400

        update_service = TeraService.get_service_by_id(json_service['id_service'])

        # Service roles
        if len(service_roles) > 0:
            # Check if there's some roles for the updated service that we need to delete
            roles_ids = [role['id_service_role'] for role in service_roles]
            id_roles_to_delete = set([role.id_service_role for role in update_service.service_roles]) \
                .difference(roles_ids)

            for id_to_del in id_roles_to_delete:
                TeraServiceRole.delete(id_todel=id_to_del)

            # Update / insert roles
            for role in service_roles:
                if role['id_service_role'] == 0:
                    # New role
                    new_role = TeraServiceRole()
                    new_role.from_json(json=role)
                    new_role.id_service = update_service.id_service
                    TeraServiceRole.insert(new_role)
                else:
                    # Update role
                    current_role = TeraServiceRole.get_service_role_by_id(role['id_service_role'])
                    if current_role.service_role_name != role['service_role_name']:
                        # OK, name was modified, update...
                        TeraServiceRole.update(role['id_service_role'], role)

        return [update_service.to_json()]

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific service',
             responses={200: 'Success',
                        400: 'Service doesn\'t exists',
                        403: 'Logged user can\'t delete service (only super admins can delete) or service is a system '
                             'service',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        if not current_user.user_superadmin:
            return gettext('Forbidden'), 403

        # Check that we are not trying to delete a system service
        service = TeraService.get_service_by_id(id_todel)
        if not service:
            return gettext('Invalid service'), 400

        if service.service_system:
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraService.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryServices.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200

