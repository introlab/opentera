from flask import request
from flask_restx import Resource, inputs  # , reqparse
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraParticipant import TeraParticipant
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from datetime import datetime

from opentera.db.models.TeraSession import TeraSession, TeraSessionStatus
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraDevice import TeraDevice

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session', type=int, help='ID of the session to query')
get_parser.add_argument('uuid_session', type=str, help='UUID of the session to query')
get_parser.add_argument('id_participant', type=int, help='ID of the participant to query')
get_parser.add_argument('id_user', type=int, help='ID of the user to query')
get_parser.add_argument('id_device', type=int, help='ID of the device to query')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')
get_parser.add_argument('with_events', type=inputs.boolean, help='Also includes session events')
get_parser.add_argument('with_session_type', type=inputs.boolean, help='Also includes session type information')
get_parser.add_argument('status', type=int, help='Limit to specific session status')
get_parser.add_argument('limit', type=int, help='Maximum number of results to return')
get_parser.add_argument('offset', type=int, help='Number of items to ignore in results, offset from 0-index')
get_parser.add_argument('start_date', type=inputs.date, help='Start date, sessions before that date will be ignored')
get_parser.add_argument('end_date', type=inputs.date, help='End date, sessions after that date will be ignored')
get_parser.add_argument('token', type=str, help='Secret Token')

post_parser = api.parser()
post_parser.add_argument('token', type=str, help='Secret Token')
post_schema = api.schema_model('user_session', {'properties': TeraSession.get_json_schema(),
                                                'type': 'object',
                                                'location': 'json'})

# delete_parser =  api.parser()
# delete_parser.add_argument('id', type=int, help='Session ID to delete', required=True)
# delete_parser.add_argument('token', type=str, help='Secret Token')


class ServiceQuerySessions(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return sessions information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        args = get_parser.parse_args()

        service_access = DBManager.serviceAccess(current_service)

        sessions = []
        if args['id_session']:
            if args['id_session'] not in service_access.get_accessible_sessions_ids():
                return gettext('Forbidden'), 403
            sessions = [TeraSession.get_session_by_id(args['id_session'])]
        elif args['uuid_session']:
            queried_session = TeraSession.get_session_by_uuid(args['uuid_session'])
            if queried_session:
                if queried_session.id_session not in service_access.get_accessible_sessions_ids():
                    return gettext('Forbidden'), 403
            sessions = [queried_session]
        elif args['id_participant']:
            if args['id_participant'] not in service_access.get_accessible_participants_ids():
                return gettext('Forbidden'), 403
            sessions = TeraSession.get_sessions_for_participant(part_id=args['id_participant'],
                                                                status=args['status'], limit=args['limit'],
                                                                offset=args['offset'], start_date=args['start_date'],
                                                                end_date=args['end_date'])
        elif args['id_user']:
            accessibles_users_ids = service_access.get_accessible_users_ids()
            if args['id_user'] not in accessibles_users_ids:
                return gettext('Forbidden'), 403
            sessions = TeraSession.get_sessions_for_user(user_id=args['id_user'], status=args['status'],
                                                         limit=args['limit'], offset=args['offset'],
                                                         start_date=args['start_date'], end_date=args['end_date'])
        elif args['id_device']:
            if args['id_device'] not in service_access.get_accessible_devices_ids():
                return gettext('Forbidden'), 403
            sessions = TeraSession.get_sessions_for_device(device_id=args['id_device'], status=args['status'],
                                                           limit=args['limit'], offset=args['offset'],
                                                           start_date=args['start_date'], end_date=args['end_date'])
        else:
            return gettext('Missing arguments: at least one id is required'), 400

        try:
            sessions_list = []
            for ses in sessions:
                session_json = ses.to_json(minimal=args['list'])

                if args['with_session_type']:
                    session_type = TeraSessionType.get_session_type_by_id(ses.id_session_type)
                    session_json['session_type'] = session_type.to_json()

                if args['with_events']:
                    # Get events for session
                    from opentera.db.models.TeraSessionEvent import TeraSessionEvent
                    session_events = TeraSessionEvent.get_events_for_session(ses.id_session)
                    session_events_json = []
                    for event in session_events:
                        session_events_json.append(event.to_json(args['list']))
                    session_json['session_events'] = session_events_json
                sessions_list.append(session_json)

            return sessions_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQuerySessions.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @api.doc(description='Create / update session. id_session must be set to "0" to create a new '
                         'session.',
             responses={200: 'Success',
                        403: 'Service can\'t create/update the specified session',
                        400: 'Badly formed JSON or missing fields(session, id_session, session_participants_ids and/or '
                             'session_users_ids[for new sessions]) in the JSON body',
                        500: 'Internal error when saving session'})
    @api.expect(post_parser)
    @api.expect(post_schema)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        if 'session' not in request.json:
            return gettext('Missing session'), 400

        json_session = request.json['session']

        # Validate if we have an id
        if 'id_session' not in json_session:
            return gettext('Missing id_session'), 400

        if 'id_service' not in json_session and json_session['id_session'] == 0:
            json_session['id_creator_service'] = current_service.id_service

        service_access = DBManager.serviceAccess(current_service)

        session_parts_uuids = []
        session_users_uuids = []
        session_devices_uuids = []
        if 'session_participants_uuids' in json_session:
            accessible_participants = service_access.get_accessible_participants()
            session_parts_uuids = json_session['session_participants_uuids']
            if set(session_parts_uuids).difference([part.participant_uuid for part in accessible_participants]):
                # At least one participant is not accessible to the service
                return gettext('Service doesn\'t have access to at least one participant of that session.'), 403
            del json_session['session_participants_uuids']
        if 'session_users_uuids' in json_session:
            accessible_users = service_access.get_accessible_users()
            session_users_uuids = json_session['session_users_uuids']
            if set(session_users_uuids).difference([user.user_uuid for user in accessible_users]):
                # At least one user is not accessible to the service
                return gettext('Service doesn\'t have access to at least one user of that session.'), 403
            del json_session['session_users_uuids']
        if 'session_devices_uuids' in json_session:
            accessible_devices = service_access.get_accessible_devices()
            session_devices_uuids = json_session['session_devices_uuids']
            if set(session_devices_uuids).difference([device.device_uuid for device in accessible_devices]):
                # At least one device is not accessible to the service
                return gettext('Service doesn\'t have access to at least one device of that session.'), 403
            del json_session['session_devices_uuids']

        # Do the update!
        if json_session['id_session'] > 0:
            # Already existing
            try:
                TeraSession.update(json_session['id_session'], json_session)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQuerySessions.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New session
            if 'id_session_type' not in json_session:
                return gettext('Missing id_session_type'), 400

            # Check for default values
            if 'session_start_datetime' not in json_session:
                json_session['session_start_datetime'] = datetime.now()

            if 'session_name' not in json_session:
                session_name = TeraSessionType.get_session_type_by_id(json_session['id_session_type']).session_type_name
                session_date = json_session['session_start_datetime']
                if not isinstance(session_date, datetime):
                    session_date = datetime.fromisoformat(json_session['session_start_datetime'])
                # session_name += ' [' + session_date.strftime('%d-%m-%Y %H:%M') + ']'
                session_name += ' [' + str(session_date.year) + '.' + str(TeraSession.get_count()) + ']'
                json_session['session_name'] = session_name

            if 'session_status' not in json_session:
                json_session['session_status'] = TeraSessionStatus.STATUS_INPROGRESS.value
            try:
                new_ses = TeraSession()
                new_ses.from_json(json_session)
                TeraSession.insert(new_ses)
                # Update ID for further use
                json_session['id_session'] = new_ses.id_session
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQuerySessions.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        update_session = TeraSession.get_session_by_id(json_session['id_session'])

        # Manage session participants
        if session_parts_uuids:
            # Add participants not already there
            current_session_part_uuids = [part.participant_uuid for part in update_session.session_participants]
            part_uuids_to_add = set(session_parts_uuids).difference(current_session_part_uuids)
            update_session.session_participants.extend([TeraParticipant.get_participant_by_uuid(part_uuid)
                                                        for part_uuid in part_uuids_to_add])

            # Then, delete participants not present in the posted list
            current_session_part_uuids.extend(list(part_uuids_to_add))
            missing_participant_uuids = set(current_session_part_uuids).difference(session_parts_uuids)
            for participant_uuid in missing_participant_uuids:
                if participant_uuid in current_session_part_uuids:
                    update_session.session_participants.remove(TeraParticipant.get_participant_by_uuid(participant_uuid))

        # Manage session users
        if session_users_uuids:
            current_session_user_uuids = [user.user_uuid for user in update_session.session_users]
            diff_uuids = set(session_users_uuids).difference(current_session_user_uuids)
            update_session.session_users.extend([TeraUser.get_user_by_uuid(user_uuid)
                                                 for user_uuid in diff_uuids])

        # Manage session devices
        if session_devices_uuids:
            current_session_device_uuids = [device.device_uuid for device in update_session.session_devices]
            diff_uuids = set(session_devices_uuids).difference(current_session_device_uuids)
            update_session.session_devices.extend([TeraDevice.get_device_by_uuid(device_uuid)
                                                   for device_uuid in diff_uuids])

        if session_users_uuids or session_parts_uuids or session_devices_uuids:
            # Commit the changes
            update_session.commit()

        return [update_session.to_json()]

    # @api.doc(description='Delete a specific session',
    #          responses={200: 'Success',
    #                     403: 'Service can\'t delete session',
    #                     500: 'Database error.'})
    # @api.expect(delete_parser)
    # @LoginModule.service_token_or_certificate_required
    # def delete(self):
    #     parser = delete_parser
    #
    #     service_access = DBManager.serviceAccess(current_service)
    #
    #     args = parser.parse_args()
    #     id_todel = args['id']
    #
    #     # Check if current service can delete
    #     # Service can delete a session if it has access to one of its participant
    #     todel_session = TeraSession.get_session_by_id(id_todel)
    #     session_parts_ids = [part.id_participant for part in todel_session.session_participants]
    #     session_users_ids = [user.id_user for user in todel_session.session_users]
    #     session_devices_ids = [device.id_device for device in todel_session.session_devices]
    #
    #     accessibles_part_ids = service_access.get_accessible_participants_ids()
    #     if set(session_parts_ids).difference(accessibles_part_ids):
    #         # At least one participant is not accessible to the user
    #         return gettext('Service doesn\'t have access to at least one participant of that session.'), 403
    #
    #     accessibles_user_ids = service_access.get_accessible_users_ids()
    #     if set(session_users_ids).difference(accessibles_user_ids):
    #         # At least one session user is not accessible to the user
    #         return gettext('Service doesn\'t have access to at least one user of that session.'), 403
    #
    #     accessibles_device_ids = service_access.get_accessible_devices_ids()
    #     if set(session_devices_ids).difference(accessibles_device_ids):
    #         # At least one session user is not accessible to the user
    #         return gettext('Service doesn\'t have access to at least one device of that session.'), 403
    #
    #     from opentera.db.models.TeraSession import TeraSessionStatus
    #     if todel_session.session_status == TeraSessionStatus.STATUS_INPROGRESS.value:
    #         return gettext('Session is in progress: can\'t delete that session.'), 403
    #
    #     # If we are here, we are allowed to delete. Do so.
    #     try:
    #         TeraSession.delete(id_todel=id_todel)
    #     except exc.SQLAlchemyError as e:
    #         import sys
    #         print(sys.exc_info())
    #         self.module.logger.log_error(self.module.module_name,
    #                                      ServiceQuerySessions.__name__,
    #                                      'delete', 500, 'Database error', str(e))
    #         return gettext('Database error'), 500
    #
    #     return '', 200
