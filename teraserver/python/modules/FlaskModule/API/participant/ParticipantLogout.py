from flask import jsonify, session
from flask_login import logout_user
from flask_restx import Resource, reqparse, fields
from flask_babel import gettext
from modules.LoginModule.LoginModule import participant_multi_auth, current_participant
from modules.FlaskModule.FlaskModule import participant_api_ns as api

# Parser definition(s)
get_parser = api.parser()


class ParticipantLogout(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Logout participant',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @participant_multi_auth.login_required
    def get(self):
        if current_participant:
            logout_user()
            session.clear()
            self.module.send_participant_disconnect_module_message(current_participant.participant_uuid)
            return gettext("Participant logged out."), 200
        else:
            return gettext("Participant not logged in"), 403
