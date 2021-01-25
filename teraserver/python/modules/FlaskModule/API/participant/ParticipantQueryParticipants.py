from flask import session
from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import participant_multi_auth
from modules.FlaskModule.FlaskModule import participant_api_ns as api
from opentera.db.models.TeraParticipant import TeraParticipant
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')

post_parser = api.parser()


class ParticipantQueryParticipants(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @participant_multi_auth.login_required(role='full')
    @api.expect(get_parser)
    @api.doc(description='Return participant information.',
             responses={200: 'Success',
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

        return current_participant.to_json(minimal=minimal)

    @participant_multi_auth.login_required(role='full')
    @api.expect(post_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def post(self):
        return gettext('Not implemented'), 501
