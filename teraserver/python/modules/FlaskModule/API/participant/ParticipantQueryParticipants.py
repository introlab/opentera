from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import participant_multi_auth, current_participant
from modules.FlaskModule.FlaskModule import participant_api_ns as api
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')

post_parser = api.parser()


class ParticipantQueryParticipants(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return participant information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @participant_multi_auth.login_required(role='limited')
    def get(self):
        """
        Get current participant informations
        """
        participant_access = DBManager.participantAccess(current_participant)
        args = get_parser.parse_args(strict=True)

        if current_participant.fullAccess:
            minimal = False
            if args['list']:
                minimal = True

            return current_participant.to_json(minimal=minimal)
        else:
            return {'participant_name': current_participant.participant_name}

    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @api.expect(post_parser)
    @participant_multi_auth.login_required(role='full')
    def post(self):
        """
        Update current participant informations
        """
        return gettext('Not implemented'), 501
