from flask import request
from flask_restx import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraServiceRole import TeraServiceRole
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from modules.DatabaseModule.DBManager import DBManager, DBManagerTeraServiceAccess
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user_group', type=int, help='Usergroup ID to query service access')

post_parser = api.parser()
post_schema = api.schema_model('service_service_access', {'properties': TeraServiceAccess.get_json_schema(),
                                                          'type': 'object',
                                                          'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific service access ID to delete. '
                                                'Be careful: this is not the service or service role ID, but the ID'
                                                ' of the association itself!', required=True)


class ServiceQueryServiceAccess(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get access roles for a specific items. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of access roles',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting association'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        service_access: DBManagerTeraServiceAccess = DBManager.serviceAccess(current_service)
        args = get_parser.parse_args()

        current_service_access = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_user_group']:
            if args['id_user_group'] in service_access.get_accessible_usergroups_ids():
                current_service_access = TeraServiceAccess.get_service_access_for_user_group(
                    id_service=current_service.id_service, id_user_group=args['id_user_group'])

        try:
            sa_list = []
            for sa in current_service_access:
                json_sa = sa.to_json()
                sa_list.append(json_sa)
            return sa_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryServiceAccess.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @api.doc(description='Create/update service - access association. A list can be posted - if an item with a '
                         'id_service_access doesn\'t have an id_service_role element, it will be deleted.',
             responses={200: 'Success',
                        403: 'Logged service can\'t modify association (only self access can be modified)',
                        400: 'Badly formed JSON or missing fields in the JSON body',
                        500: 'Internal error occurred when saving association'},
             params={'token': 'Secret token'})
    @api.expect(post_schema)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        service_access: DBManagerTeraServiceAccess = DBManager.serviceAccess(current_service)

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
                if json_sa['id_device'] not in service_access.get_accessible_devices_ids(admin_only=True):
                    return gettext('Forbidden'), 403

            if 'id_participant_group' in json_sa:
                if json_sa['id_participant_group'] not in service_access.get_accessible_participants_groups_ids():
                    return gettext('Forbidden'), 403

            if 'id_user_group' in json_sa:
                if json_sa['id_user_group'] not in service_access.get_accessible_usergroups_ids():
                    return gettext('Forbidden'), 403

            if 'id_service_role' in json_sa:
                if json_sa['id_service_role'] != '':
                    role = TeraServiceRole.get_service_role_by_id(json_sa['id_service_role'])
                    if not role:
                        return gettext('Bad id_service_role'), 400
                    if role.id_service != current_service.id_service:
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
                                                     ServiceQueryServiceAccess.__name__,
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
                                                 ServiceQueryServiceAccess.__name__,
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
                                                 ServiceQueryServiceAccess.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        return json_sa_list

    @api.doc(description='Delete a specific service access.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete association (not related to this service)',
                        500: 'Association not found or database error.'},
             params={'token': 'Secret token'})
    @api.expect(delete_parser)
    @LoginModule.service_token_or_certificate_required
    def delete(self):
        service_access: DBManagerTeraServiceAccess = DBManager.serviceAccess(current_service)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current service can delete
        todel_access = TeraServiceAccess.get_service_access_by_id(id_todel)
        if not todel_access:
            return gettext('Not found'), 400

        if todel_access.service_access_role.id_service != current_service.id_service:
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceAccess.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryServiceAccess.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
