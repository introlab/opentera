from flask import jsonify, session, request
from flask_restplus import Resource, reqparse, inputs, fields
from libtera.db.models.TeraSession import TeraSession
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.DBManager import DBManager
from modules.LoginModule.LoginModule import LoginModule
from sqlalchemy import exc
from flask_babel import gettext
from sqlalchemy.exc import InvalidRequestError
from modules.FlaskModule.FlaskModule import device_api_ns as api
from libtera.db.models.TeraDevice import TeraDevice


# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('token', type=str, help='Secret Token')
get_parser.add_argument('id_session', type=int, help='Session ID')
# get_parser.add_argument('id_participant', type=int, help='Participant ID')
get_parser.add_argument('list', type=inputs.boolean, help='List all sessions')

post_parser = api.parser()
post_parser.add_argument('token', type=str, help='Secret Token')
post_parser.add_argument('session', type=str, location='json', help='Session to create / update', required=True)

session_schema = api.schema_model('session', {
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
                    'contains': {
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


class DeviceQuerySessions(Resource):

    def __init__(self, _api, flaskModule=None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @LoginModule.token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Get session',
             responses={200: 'Success',
                        400: 'Required parameter is missing',
                        500: 'Internal server error',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def get(self):

        current_device = TeraDevice.get_device_by_uuid(session['_user_id'])
        device_access = DBManager.deviceAccess(current_device)
        args = get_parser.parse_args(strict=True)

        # Get all sessions
        sessions = device_access.get_accessible_sessions()

        # Can't query sessions, unless we have a parameter!
        if not any(args.values()):
            return '', 400

        elif args['id_session']:
            sessions = device_access.query_session(session_id=args['id_session'])
        try:
            sessions_list = []
            for ses in sessions:
                if args['list'] is None:
                    session_json = ses.to_json()
                    sessions_list.append(session_json)
                else:
                    session_json = ses.to_json(minimal=True)
                    sessions_list.append(session_json)

            return sessions_list

        except InvalidRequestError:
            return '', 500

    @LoginModule.token_or_certificate_required
    @api.expect(session_schema, validate=True)
    @api.doc(description='Update/Create session',
             responses={200: 'Success',
                        400: 'Required parameter is missing',
                        500: 'Internal server error',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def post(self):
        current_device = TeraDevice.get_device_by_uuid(session['_user_id'])

        args = post_parser.parse_args()

        # Using request.json instead of parser, since parser messes up the json!
        if 'session' not in request.json:
            return '', 400

        json_session = request.json['session']

        device_access = DBManager.deviceAccess(current_device)

        # Validate if we have an id
        if 'id_session' not in json_session:
            return '', 400

        # Validate that we have session participants for new sessions
        if 'session_participants' not in json_session and json_session['id_session'] == 0:
            return '', 400

        # We know we have a device
        # Avoid identity thief
        json_session['id_creator_device'] = current_device.id_device

        # Validate session type
        session_types = device_access.get_accessible_session_types_ids()

        if not json_session['id_session_type'] in session_types:
            return '', 403

        # Do the update!
        if json_session['id_session'] > 0:

            # Already existing
            # TODO handle participant list (remove, add) in session
            try:
                if 'session_participants' in json_session:
                    participants = json_session.pop('session_participants')
                    print('removing participants', participants)

                TeraSession.update(json_session['id_session'], json_session)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_ses = TeraSession()
                participants = json_session.pop('session_participants')
                new_ses.from_json(json_session)

                for uuid in participants:
                    participant = TeraParticipant.get_participant_by_uuid(uuid)
                    new_ses.session_participants.append(participant)

                TeraSession.insert(new_ses)
                # Update ID for further use
                json_session['id_session'] = new_ses.id_session

            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_session = TeraSession.get_session_by_id(json_session['id_session'])

        return jsonify(update_session.to_json())

    @LoginModule.token_or_certificate_required
    def delete(self):
        return '', 403
