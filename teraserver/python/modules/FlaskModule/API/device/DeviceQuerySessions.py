from flask import jsonify, session, request
from flask_restx import Resource, inputs
from flask_babel import gettext
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraParticipant import TeraParticipant
from modules.DatabaseModule.DBManager import DBManager
from modules.LoginModule.LoginModule import LoginModule
from sqlalchemy import exc
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice
import datetime

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('token', type=str, help='Secret Token')
get_parser.add_argument('id_session', type=int, help='Session ID')
get_parser.add_argument('list', type=inputs.boolean, help='List all sessions')

post_parser = api.parser()
post_parser.add_argument('token', type=str, help='Secret Token')
post_parser.add_argument('session', type=str, location='json', help='Session to create / update', required=True)

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


class DeviceQuerySessions(Resource):

    def __init__(self, _api, flaskModule=None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @LoginModule.device_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Get session',
             responses={403: 'Forbidden for security reasons.'})
    def get(self):

        # current_device = TeraDevice.get_device_by_uuid(session['_user_id'])
        # device_access = DBManager.deviceAccess(current_device)
        # args = get_parser.parse_args(strict=True)
        #
        # # Get all sessions
        # sessions = device_access.get_accessible_sessions()
        #
        # # Can't query sessions, unless we have a parameter!
        # if not any(args.values()):
        #     return '', 400
        #
        # elif args['id_session']:
        #     sessions = device_access.query_session(session_id=args['id_session'])
        # try:
        #     sessions_list = []
        #     for ses in sessions:
        #         if args['list'] is None:
        #             session_json = ses.to_json()
        #             sessions_list.append(session_json)
        #         else:
        #             session_json = ses.to_json(minimal=True)
        #             sessions_list.append(session_json)
        #
        #     return sessions_list
        #
        # except InvalidRequestError:
        #     return '', 500
        return gettext('Forbidden for security reasons'), 403

    @LoginModule.device_token_or_certificate_required
    @api.expect(session_schema, validate=True)
    @api.doc(description='Update/Create session',
             responses={200: 'Success',
                        400: 'Required parameter is missing',
                        500: 'Internal server error',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def post(self):
        current_device = TeraDevice.get_device_by_uuid(session['_user_id'])
        # current_device = TeraDevice.get_device_by_id(4) #  For tests only

        args = post_parser.parse_args()

        # Using request.json instead of parser, since parser messes up the json!
        if 'session' not in request.json:
            return gettext('Missing arguments'), 400

        json_session = request.json['session']

        device_access = DBManager.deviceAccess(current_device)

        # Validate if we have an id
        if 'id_session' not in json_session:
            return gettext('Missing arguments'), 400

        # Validate if we have an id
        if 'id_session_type' not in json_session:
            return gettext('Missing arguments'), 400

        # Validate that we have session participants or users for new sessions
        if ('session_participants' not in json_session and 'session_users' not in json_session) \
                and json_session['id_session'] == 0:
            return gettext('Missing arguments'), 400

        # We know we have a device
        # Avoid identity thief
        json_session['id_creator_device'] = current_device.id_device

        # Validate session type
        session_types = device_access.get_accessible_session_types_ids()

        if not json_session['id_session_type'] in session_types:
            return gettext('Unauthorized'), 403

        # Check if a session of that type and name already exists. If so, don't create it, just returns it.
        if json_session['id_session'] == 0:
            if 'session_name' not in json_session:
                return gettext('Missing argument \'session name\''), 400
            if 'session_start_datetime' not in json_session:
                return gettext('Missing argument \'session_start_datetime\''), 400

            existing_session = device_access.query_existing_session(session_name=json_session['session_name'],
                                                                    session_type_id=json_session['id_session_type'],
                                                                    session_date=datetime.datetime.fromisoformat(
                                                                        json_session['session_start_datetime']),
                                                                    participant_uuids=
                                                                    json_session['session_participants']
                                                                    )
            if existing_session:
                json_session['id_session'] = existing_session.id_session
                # Don't change session start datetime
                json_session['session_start_datetime'] = existing_session.session_start_datetime.isoformat()
        else:
            # Existing session - check if we can access it
            if json_session['id_session'] not in device_access.get_accessible_sessions_ids():
                return gettext('Unauthorized', 403)

        # Do the update!
        if json_session['id_session'] > 0:

            # Already existing
            # TODO handle participant list (remove, add) in session
            try:
                if 'session_participants' in json_session:
                    participants = json_session.pop('session_participants')
                    print('removing participants', participants)

                TeraSession.update(json_session['id_session'], json_session)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             DeviceQuerySessions.__name__,
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
                    new_ses.session_participants.append(participant)

                if len(participants) > 0:
                    new_ses.commit()   # Commits added participants

                # Update ID for further use
                json_session['id_session'] = new_ses.id_session

            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info(), e)
                self.module.logger.log_error(self.module.module_name,
                                             DeviceQuerySessions.__name__,
                                             'post', 500, 'Database error', str(e))
                return '', 500

        update_session = TeraSession.get_session_by_id(json_session['id_session'])

        return jsonify(update_session.to_json())

    @LoginModule.device_token_or_certificate_required
    def delete(self):
        return gettext('Forbidden for security reasons'), 403
