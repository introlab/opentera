from flask import request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraSessionTypeServices import TeraSessionTypeServices
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraService import TeraService
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc, inspect
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session_type', type=int, help='Session type ID to query secondary services')

get_parser.add_argument('with_services', type=inputs.boolean, help='Used with id_session_type. Also return services '
                                                                   'that don\'t have any association with that type')

get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')

post_parser = api.parser()
post_schema = api.schema_model('user_session_type_services', {'properties': TeraSessionTypeServices.get_json_schema(),
                                                             'type': 'object',
                                                             'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific session-type - service association ID to delete. '
                                                'Be careful: this is not the session-type or service ID, but the ID'
                                                ' of the association itself!', required=True)


class UserQuerySessionTypeServices(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get session types secondary services association. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of session-types - services association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting association'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        """
        Get session types additional association with services
        """
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

        session_type_sessions = []
        # If we have no arguments, return error
        if not any(args.values()) and not args['id_session_type']:
            return gettext('Missing arguments'), 400

        session_type_services = []
        if args['id_session_type']:
            if args['id_session_type'] in user_access.get_accessible_session_types_ids():
                session_type_services = user_access.query_secondary_services_for_session_type(
                    session_type_id=args['id_session_type'], include_other_services=args['with_services'])
        try:
            sts_list = []
            for sts in session_type_services:
                json_sts = sts.to_json()
                if args['list'] is None:
                    obj_type = inspect(sts)
                    if not obj_type.transient:
                        json_sts['session_type_name'] = sts.session_type_service_session_type.session_type_name
                        json_sts['service_name'] = sts.session_type_service_service.service_name
                    else:
                        # Temporary object, a not-committed object, result of listing projects not associated to a
                        # session type.
                        if sts.id_session_type:
                            st: TeraSessionType = TeraSessionType.get_session_type_by_id(sts.id_session_type)
                            json_sts['session_type_name'] = st.session_type_name
                        else:
                            json_sts['session_type_name'] = None
                        if sts.id_service:
                            service = TeraService.get_service_by_id(sts.id_service)
                            json_sts['service_name'] = service.service_name
                        else:
                            json_sts['service_name'] = None
                sts_list.append(json_sts)

            return sts_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessionTypeServices.__name__,
                                         'get', 500, 'InvalidRequestError', e)
            return '', 500

    @api.doc(description='Create/update session-type - service additional association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify association',
                        400: 'Badly formed JSON or missing fields(id_service or id_session_type) in the JSON body',
                        500: 'Internal error occurred when saving association'})
    @api.expect(post_schema)
    @user_multi_auth.login_required
    def post(self):
        """
        Create / update session types - service additional association
        """
        user_access = DBManager.userAccess(current_user)
        accessible_service_ids = user_access.get_accessible_services_ids(admin_only=True)
        if 'session_type' in request.json:
            # We have a session_type. Get list of items
            if 'id_session_type' not in request.json['session_type']:
                return gettext('Missing id_session_type'), 400
            if 'services' not in request.json['session_type']:
                return gettext('Missing services'), 400
            id_session_type = request.json['session_type']['id_session_type']

            if id_session_type not in user_access.get_accessible_session_types_ids(admin_only=True):
                return gettext("Access denied"), 403

            # Get all current association for session type
            current_services = TeraSessionTypeServices.get_services_for_session_type(session_type_id=id_session_type)
            current_services_ids = [service.id_service for service in current_services]
            received_service_ids = [service['id_service'] for service in request.json['session_type']['services']]
            # Difference - we must delete services not anymore in the list
            todel_ids = set(current_services_ids).difference(received_service_ids)
            # Also filter services already there
            # received_service_ids = set(received_service_ids).difference(current_services_ids)
            try:
                for service_id in todel_ids:
                    if service_id in accessible_service_ids:  # Don't remove from the list if not admin for that project!
                        TeraSessionTypeServices.delete_with_ids(session_type_id=id_session_type, service_id=service_id,
                                                                autocommit=False)
                TeraSessionTypeServices.commit()
            except exc.IntegrityError as e:
                self.module.logger.log_warning(self.module.module_name, UserQuerySessionTypeServices.__name__, 'delete',
                                               400, 'Integrity error', str(e))
                return gettext('Can\'t remove associated service from session type: please delete all sessions using '
                               'that type before deleting.'), 400
            # Build services association to add
            json_sts = [{'id_session_type': id_session_type, 'id_service': service_id}
                        for service_id in received_service_ids]
        elif 'service' in request.json:
            # We have a service. Get list of items
            if 'id_service' not in request.json['service']:
                return gettext('Missing service ID'), 400
            if 'sessiontypes' not in request.json['service']:
                return gettext('Missing session types'), 400
            id_service = request.json['service']['id_service']

            # Check if admin for that project
            if id_service not in accessible_service_ids:
                return gettext('Access denied'), 403

            # Get all current service association for session type
            current_session_types = TeraSessionTypeServices.get_sessions_types_for_service(service_id=id_service)
            current_session_types_ids = [st.id_session_type for st in current_session_types]
            received_st_ids = [st['id_session_type'] for st in request.json['service']['sessiontypes']]
            # Difference - we must delete types not anymore in the list
            todel_ids = set(current_session_types_ids).difference(received_st_ids)
            # Also filter session types already there
            received_st_ids = set(received_st_ids).difference(current_session_types_ids)
            try:
                for st_id in todel_ids:
                    TeraSessionTypeServices.delete_with_ids(session_type_id=st_id, service_id=id_service,
                                                            autocommit=False)
                TeraSessionTypeServices.commit()
            except exc.IntegrityError as e:
                self.module.logger.log_warning(self.module.module_name, UserQuerySessionTypeServices.__name__, 'delete',
                                               500, 'Integrity error', str(e))
                return gettext('Can\'t remove session type association from service: please delete all sessions using '
                               'that type before deleting.'), 500

            # Build associations to add
            json_sts = [{'id_session_type': st_id, 'id_service': id_service} for st_id in received_st_ids]
        elif 'session_type_service' in request.json:
            json_sts = request.json['session_type_service']
            if not isinstance(json_sts, list):
                json_sts = [json_sts]
        else:
            return gettext('Unknown format'), 400

        # Validate if we have an id and access
        for json_st in json_sts:
            if 'id_session_type' not in json_st or 'id_service' not in json_st:
                return gettext('Badly formatted request'), 400

            if json_st['id_service'] not in accessible_service_ids:
                return gettext('Forbidden'), 403

            if 'id_session_type_service' not in json_st:
                # Check if already exists
                st = TeraSessionTypeServices. \
                    get_session_type_service_for_session_type_service(service_id=int(json_st['id_service']),
                                                                      session_type_id=int(json_st['id_session_type']))
                if st:
                    json_st['id_session_type_service'] = st.id_session_type_service
                else:
                    json_st['id_session_type_service'] = 0

            # Do the update!
            if int(json_st['id_session_type_service']) > 0:
                pass
            else:
                try:
                    new_sts = TeraSessionTypeServices()
                    new_sts.from_json(json_st)
                    new_sts = TeraSessionTypeServices.insert(new_sts)
                    # Update ID for further use
                    json_st['id_session_type_service'] = new_sts.id_session_type_service
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQuerySessionTypeServices.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        return json_sts

    @api.doc(description='Delete a specific session-type - service additional association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete association (no access to session-type or project)',
                        400: 'Association not found (invalid id?)'})
    @api.expect(delete_parser)
    @user_multi_auth.login_required
    def delete(self):
        """
        Delete specific session-type - service additional association
        """
        user_access = DBManager.userAccess(current_user)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        sts = TeraSessionTypeServices.get_session_type_service_by_id(id_todel)
        if not sts:
            return gettext('Not found'), 404

        if sts.id_session_type not in user_access.get_accessible_session_types_ids(admin_only=True):
            return gettext('Access denied'), 403

        if sts.id_service not in user_access.get_accessible_services_ids(admin_only=True):
            return gettext('Access denied'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSessionTypeServices.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting:
            # - Associated project still have sessions of that type
            self.module.logger.log_warning(self.module.module_name, UserQuerySessionTypeServices.__name__, 'delete',
                                           500, 'Integrity error', str(e))
            return gettext('Can\'t remove associated service from session type: please delete all sessions of that type'
                           ' before deleting.'), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessionTypeServices.__name__,
                                         'delete', 500, 'Database error', e)
            return gettext('Database error'), 500

        return '', 200