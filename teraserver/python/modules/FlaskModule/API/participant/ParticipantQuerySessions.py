from flask import request
from flask_restx import Resource, inputs
from flask_babel import gettext
from sqlalchemy import exc
from modules.LoginModule.LoginModule import participant_multi_auth, current_participant
from modules.FlaskModule.FlaskModule import participant_api_ns as api
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSession import TeraSession
from modules.DatabaseModule.DBManager import DBManager

import datetime

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session', type=int, help='ID of the session to query')
get_parser.add_argument('session_uuid', type=str, help='Session UUID to query')
get_parser.add_argument('status', type=int, help='Limit to specific session status')
get_parser.add_argument('limit', type=int, help='Maximum number of results to return')
get_parser.add_argument('offset', type=int, help='Number of items to ignore in results, offset from 0-index')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')
get_parser.add_argument('status', type=int, help='Limit to specific session status')
get_parser.add_argument('start_date', type=inputs.date, help='Start date, sessions before that date will be ignored')
get_parser.add_argument('end_date', type=inputs.date, help='End date, sessions after that date will be ignored')

session_schema = api.schema_model('device_session', {
    'properties': {
        'session': {
            'type': 'object',
            'properties': {
                'id_session': {
                    'type': 'integer'
                },
                'session_participants': {
                    'type': 'array',
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'format': 'uuid'
                    }
                },
                'id_session_type': {
                    'type': 'integer'
                },
                'session_name': {
                    'type': 'string'
                },
                'session_status': {
                    'type': 'integer'
                },
                'session_start_datetime': {
                    'type': 'string'
                }
            },
            'required': ['id_session', 'session_participants',
                         'id_session_type', 'session_name', 'session_status', 'session_start_datetime']
        },

    },
    'type': 'object',
    'required': ['session']
})


class ParticipantQuerySessions(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @participant_multi_auth.login_required(role='full')
    @api.expect(get_parser)
    @api.doc(description='Get session associated with participant.',
             responses={200: 'Success',
                        400: 'Bad request',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        """
        Get participant sessions
        """
        participant_access = DBManager.participantAccess(current_participant)
        args = get_parser.parse_args(strict=True)

        minimal = False
        if args['list']:
            minimal = True

        filters = {}
        if args['id_session']:
            filters['id_session'] = args['id_session']

        if args['session_uuid']:
            filters['session_uuid'] = args['session_uuid']

        # List comprehension, get all sessions with filter
        sessions_list = [data.to_json(minimal=minimal) for data in TeraSession.get_sessions_for_participant(
            part_id=current_participant.id_participant, status=args['status'], limit=args['limit'],
            offset=args['offset'], start_date=args['start_date'], end_date=args['end_date'], filters=filters)]

        return sessions_list

    @api.doc(description='Update/Create session',
             responses={200: 'Success',
                        400: 'Required parameter is missing',
                        500: 'Internal server error',
                        501: 'Not implemented',
                        403: 'Logged participant doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(session_schema)
    @participant_multi_auth.login_required(role='limited')
    def post(self):
        """
        Create / update a session
        """
        # args = post_parser.parse_args()
        # Using request.json instead of parser, since parser messes up the json!
        if 'session' not in request.json:
            return gettext('Missing session'), 400

        json_session = request.json['session']

        participant_access = DBManager.participantAccess(current_participant)

        # Validate if we have an id
        if 'id_session' not in json_session:
            return gettext('Missing id_session value'), 400

        # Validate if we have an id
        if 'id_session_type' not in json_session:
            return gettext('Missing id_session_type value'), 400

        # Validate that we have people in a new sessions
        if ('session_participants' not in json_session and 'session_users' not in json_session) \
                and 'session_devices' not in json_session and json_session['id_session'] == 0:
            return gettext('Missing session participants and/or users and/or devices'), 400

        # We know we have a participant,avoid identity thief
        json_session['id_creator_participant'] = current_participant.id_participant

        # Validate session type
        session_types = participant_access.get_accessible_session_types_ids()

        if not json_session['id_session_type'] in session_types:
            return gettext('No access to session type'), 403

        # Check if a session of that type and name already exists. If so, don't create it, just returns it.
        if json_session['id_session'] == 0:
            if 'session_name' not in json_session:
                return gettext('Missing argument \'session name\''), 400
            if 'session_start_datetime' not in json_session:
                return gettext('Missing argument \'session_start_datetime\''), 400

            existing_session = participant_access.query_existing_session(
                session_name=json_session['session_name'],
                session_type_id=json_session['id_session_type'],
                session_date=datetime.datetime.fromisoformat(json_session['session_start_datetime']),
                participant_uuids=json_session['session_participants']
            )

            if existing_session:
                json_session['id_session'] = existing_session.id_session
                # Don't change session start datetime
                json_session['session_start_datetime'] = existing_session.session_start_datetime.isoformat()
        else:
            # Existing session - check if we can access it
            if json_session['id_session'] not in participant_access.get_accessible_sessions_ids():
                return gettext('Unauthorized'), 403

        # Do the update!
        if json_session['id_session'] > 0:

            # Already existing
            # TODO handle participant list (remove, add) in session

            try:
                if 'session_participants' in json_session:
                    participants = json_session.pop('session_participants')

                TeraSession.update(json_session['id_session'], json_session)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ParticipantQuerySessions.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_ses = TeraSession()
                participants = json_session.pop('session_participants')
                new_ses.from_json(json_session)

                TeraSession.insert(new_ses)

                for p_uuid in participants:
                    participant = TeraParticipant.get_participant_by_uuid(p_uuid)
                    if participant is None:
                        return gettext('Invalid participant uuid'), 400
                    new_ses.session_participants.append(participant)

                if len(participants) > 0:
                    new_ses.commit()  # Commits added participants

                # Update ID for further use
                json_session['id_session'] = new_ses.id_session

            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info(), e)
                self.module.logger.log_error(self.module.module_name,
                                             ParticipantQuerySessions.__name__,
                                             'post', 500, 'Database error', str(e))
                return '', 500

        update_session = TeraSession.get_session_by_id(json_session['id_session'])

        return update_session.to_json()
