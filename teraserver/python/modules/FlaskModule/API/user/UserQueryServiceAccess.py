from flask import jsonify, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraServiceAccess import TeraServiceAccess
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user_group', type=int, help='Usergroup ID to query service access')
get_parser.add_argument('id_participant_group', type=int, help='Participant group ID to query service access')
get_parser.add_argument('id_device', type=int, help='Device ID to query service access')
get_parser.add_argument('id_service', type=int, help='Service ID to query associated access from')

post_schema = api.schema_model('user_service_access', {'properties': TeraServiceAccess.get_json_schema(),
                                                       'type': 'object',
                                                       'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific service access ID to delete. '
                                                'Be careful: this is not the service or service role ID, but the ID'
                                                ' of the association itself!', required=True)


class UserQueryServiceAccess(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get access roles for a specific items. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of access roles',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting association'})
    def get(self):
        from libtera.db.models.TeraServiceAccess import TeraServiceAccess
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        service_access = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_user_group']:
            if args['id_user_group'] in user_access.get_accessible_users_groups_ids():
                service_access = user_access.query_service_access(user_group_id=args['id_user_group'])
        elif args['id_participant_group']:
            if args['id_participant_group'] in user_access.get_accessible_groups_ids():
                service_access = user_access.query_service_access(participant_group_id=args['id_participant_group'])
        elif args['id_device']:
            if args['id_device'] in user_access.get_accessible_devices_ids():
                service_access = user_access.query_service_access(device_id=args['id_device'])
        elif args['id_service']:
            if args['id_service'] in user_access.get_accessible_services_ids():
                service_access = user_access.query_service_access(service_id=args['id_service'])

        # Sort by service
        service_access.sort(key=lambda x: x.service_access_role.id_service)
        try:
            sa_list = []
            for sa in service_access:
                json_sa = sa.to_json()
                sa_list.append(json_sa)
            return sa_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryServiceAccess.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create/update service - access association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify association (only site admin can modify association)',
                        400: 'Badly formed JSON or missing fields(id_project or id_service) in the JSON body',
                        500: 'Internal error occured when saving association'})
    def post(self):
        from libtera.db.models.TeraServiceRole import TeraServiceRole
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        if 'service_access' in request.json:
            json_sa_list = request.json['service_access']
            if not isinstance(json_sa_list, list):
                json_sa_list = [json_sa_list]
        else:
            return gettext('Missing service_access'), 400

        for json_sa in json_sa_list:
            if 'id_service_access' not in json_sa:
                return gettext('Missing id_service_access'), 400

            if ('id_participant_group' in json_sa and ('id_device' in json_sa or 'id_user_group' in json_sa)) \
                    or ('id_user_group' in json_sa and 'id_device' in json_sa):
                return gettext('Can\'t combine id_user_group, id_participant_group and id_device in request'), 400

            # Validate if we can modify
            if 'id_device' in json_sa:
                if json_sa['id_device'] not in user_access.get_accessible_devices_ids(admin_only=True):
                    return gettext('Forbidden'), 403

            if 'id_participant_group' in json_sa:
                if json_sa['id_participant_group'] not in user_access.get_accessible_groups_ids(
                        admin_only=True):
                    return gettext('Forbidden'), 403

            if 'id_user_group' in json_sa:
                if json_sa['id_user_group'] not in user_access.get_accessible_users_groups_ids(admin_only=True):
                    return gettext('Forbidden'), 403

            if 'id_service_role' in json_sa:
                if json_sa['id_service_role'] != '':
                    role = TeraServiceRole.get_service_role_by_id(json_sa['id_service_role'])
                    if not role:
                        return gettext('Bad id_service_role'), 400
                    if role.id_service not in user_access.get_accessible_services_ids(admin_only=True):
                        return gettext('Forbidden'), 403

        for json_sa in json_sa_list:
            # Do the update!
            if json_sa['id_service_access'] > 0:
                remove_access = False
                if 'id_service_role' not in json_sa:
                    remove_access = True
                else:
                    if json_sa['id_service_role'] == '':
                        remove_access = True

                if remove_access:
                    # We must remove the specified access
                    try:
                        TeraServiceAccess.delete(id_todel=json_sa['id_service_access'])
                    except exc.SQLAlchemyError as e:
                        import sys
                        print(sys.exc_info())
                        self.module.logger.log_error(self.module.module_name,
                                                     UserQueryServiceAccess.__name__,
                                                     'post', 500, 'Database error', str(e))
                        return gettext('Database error'), 500
                    continue

                # Updating
                try:
                    TeraServiceAccess.update(json_sa['id_service_access'], json_sa)
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryServiceAccess.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500
            else:
                # New
                if 'id_service_role' not in json_sa:
                    return gettext('Missing id_service_role'), 400

                if 'id_participant_group' not in json_sa and 'id_user_group' not in json_sa \
                        and 'id_device' not in json_sa:
                    return gettext('Missing at least one id field'), 400

                try:
                    new_sa = TeraServiceAccess()
                    new_sa.from_json(json_sa)
                    TeraServiceAccess.insert(new_sa)
                    # Update ID for further use
                    json_sa['id_service_access'] = new_sa.id_service_access
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryServiceAccess.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        return json_sa_list

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific service access.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete association (not admin of the associated elements)',
                        500: 'Association not found or database error.'})
    def delete(self):
        parser = delete_parser
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        todel_access = TeraServiceAccess.get_service_access_by_id(id_todel)
        if not todel_access:
            return gettext('Not found'), 400

        if todel_access.service_access_role.id_service not \
                in user_access.get_accessible_services_ids(include_system_services=False):
            return gettext('Forbidden'), 403

        if todel_access.id_user_group:
            if todel_access.id_user_group not in user_access.get_accessible_users_groups_ids(admin_only=True):
                return gettext('Forbidden'), 403

        if todel_access.id_participant_group:
            if todel_access.id_participant_group not in user_access.get_accessible_groups_ids(admin_only=True):
                return gettext('Forbidden'), 403

        if todel_access.id_device:
            if todel_access.id_device not in user_access.get_accessible_devices_ids(admin_only=True):
                return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceAccess.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryServiceAccess.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
