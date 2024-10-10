from flask import request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServiceRole import TeraServiceRole
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_service', type=int, help='Specific service ID to query roles for')
get_parser.add_argument('globals', type=inputs.boolean, help='Only return global roles, e.g. not related to a site or '
                                                             'a project')
get_parser.add_argument('list', type=inputs.boolean, help='Return minimal information about the roles')

post_parser = api.parser()
post_schema = api.schema_model('service_role', {'properties': TeraServiceRole.get_json_schema(), 'type': 'object',
                                                'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific service role ID to delete.', required=True)


class UserQueryServiceRole(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get service roles for either a specific service or for all available services.',
             responses={200: 'Success - returns list of service roles',
                        500: 'Error when getting roles'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        """
        Get service roles
        """
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

        service_roles = []
        if args['id_service']:
            if args['id_service'] in user_access.get_accessible_services_ids():
                if not args['id_service'] == TeraService.get_openteraserver_service().id_service:  # Ignore teraserver
                    service_roles = TeraServiceRole.get_service_roles(service_id=args['id_service'],
                                                                      globals_only=args['globals'])
        else:
            for id_service in user_access.get_accessible_services_ids():
                if not args['id_service'] == TeraService.get_openteraserver_service().id_service:  # Ignore teraserver
                    service_roles.extend(TeraServiceRole.get_service_roles(service_id=id_service,
                                                                           globals_only=args['globals']))

        try:
            sr_list = []
            for sr in service_roles:
                json_sr = sr.to_json(minimal=args['list'])
                sr_list.append(json_sr)
            return sr_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryServiceRole.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @api.doc(description='Create/update service role.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify service role (only super admin)',
                        400: 'Badly formed JSON or missing fields(id_service or id_service_role) in the JSON body',
                        500: 'Internal error occurred when saving association'})
    @api.expect(post_schema)
    @user_multi_auth.login_required
    def post(self):
        """
        Create / update service roles
        """
        if not current_user.user_superadmin:
            return gettext('Forbidden'), 403

        json_service_role = request.json['service_role']

        # Validate fields
        if 'id_service_role' not in json_service_role:
            return gettext('Missing id_service_role'), 400

        # Do the update / insert
        if json_service_role['id_service_role'] != 0:
            # Updating
            try:
                TeraServiceRole.update(json_service_role['id_service_role'], json_service_role)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryServiceRole.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
            update_role = TeraServiceRole.get_service_role_by_id(json_service_role['id_service_role'])
            json_service_role = update_role.to_json()
        else:
            # New
            try:
                missing_fields = TeraServiceRole.validate_required_fields(json_data=json_service_role)
                if missing_fields:
                    return gettext('Missing fields') + ': ' + str([field for field in missing_fields]), 400

                new_sr = TeraServiceRole()
                new_sr.from_json(json_service_role)
                TeraServiceRole.insert(new_sr)
                # Update ID for further use
                json_service_role['id_service_role'] = new_sr.id_service_role
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryServiceRole.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        return json_service_role

    @api.doc(description='Delete a specific service role.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete role (not super admin)',
                        500: 'Database error.'})
    @api.expect(delete_parser)
    @user_multi_auth.login_required
    def delete(self):
        """
        Delete service role
        """
        user_access = DBManager.userAccess(current_user)
        args = delete_parser.parse_args()
        id_todel = args['id']

        if not current_user.user_superadmin:
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceRole.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryServiceRole.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
