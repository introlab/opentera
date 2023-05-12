from flask import request
from flask_restx import Resource, reqparse
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from opentera.db.models.TeraServiceRole import TeraServiceRole
from sqlalchemy import exc

# Parser definition(s)
get_parser = api.parser()

post_parser = api.parser()
post_schema = api.schema_model('service_role', {'properties': TeraServiceRole.get_json_schema(), 'type': 'object',
                                                'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Service role to delete', required=True)


class ServiceQueryRoles(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get service roles for that service',
             responses={200: 'Success - returns list of roles',
                        500: 'Database error'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        args = get_parser.parse_args()
        roles = TeraServiceRole.get_service_roles(service_id=current_service.id_service)
        roles_list = []
        for role in roles:
            role_json = role.to_json()
            roles_list.append(role_json)
        return roles_list

    @api.doc(description='Create / update service roles.',
             responses={200: 'Success',
                        400: 'Badly formed JSON or missing fields in the JSON body',
                        500: 'Internal error when saving roles'},
             params={'token': 'Secret token'})
    @api.expect(post_schema)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        # Using request.json instead of parser, since parser messes up the json!
        if 'service_role' not in request.json:
            return gettext('Missing service_role field'), 400

        json_service_role = request.json['service_role']

        # Validate required fields
        if 'id_service_role' not in json_service_role:
            return gettext('Missing id_service_role'), 400

        # Always force id to this service
        json_service_role['id_service'] = current_service.id_service

        if json_service_role['id_service_role'] != 0:
            # Updating
            try:
                TeraServiceRole.update(json_service_role['id_service_role'], json_service_role)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryRoles.__name__,
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
                                             ServiceQueryRoles.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        return json_service_role

    @api.doc(description='Delete a specific service role.',
             responses={200: 'Success',
                        403: 'Logged service can\'t delete role (not related to that service)',
                        500: 'Database error.'},
             params={'token': 'Secret token'})
    @api.expect(delete_parser)
    @LoginModule.service_token_or_certificate_required
    def delete(self):
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if role is related to that service
        role: TeraServiceRole = TeraServiceRole.get_service_role_by_id(id_todel)
        if role.id_service != current_service.id_service:
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceRole.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryRoles.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
