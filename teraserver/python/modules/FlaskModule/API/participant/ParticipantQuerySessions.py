from flask import jsonify, session
from flask_restplus import Resource, reqparse, fields, inputs
from modules.LoginModule.LoginModule import participant_multi_auth
from modules.FlaskModule.FlaskModule import participant_api_ns as api
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.DBManagerTeraParticipantAccess import DBManagerTeraParticipantAccess
from libtera.db.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session', type=int, help='ID of the session to query')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')

post_parser = api.parser()


class ParticipantQuerySessions(Resource):

    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @participant_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get session associated with participant.',
             responses={200: 'Success',
                        400: 'Bad request',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        current_participant = TeraParticipant.get_participant_by_uuid(session['_user_id'])
        participant_access = DBManager.participantAccess(current_participant)

        args = get_parser.parse_args(strict=True)

        minimal = False
        if args['list']:
            minimal = True

        filters = {}
        if args['id_session']:
            filters['id_session'] = args['id_session']

        # List comprehension, get all sessions with filter
        sessions_list = [data.to_json(minimal=minimal) for data in participant_access.query_session(filters)]

        return sessions_list

    @participant_multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def post(self):
        return '', 501
