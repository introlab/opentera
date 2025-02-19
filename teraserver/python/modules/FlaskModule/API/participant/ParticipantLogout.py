from flask import session, request
from flask_login import logout_user
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import participant_multi_auth, current_participant, LoginModule
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
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @participant_multi_auth.login_required
    def get(self):
        """
        Participant logout
        """
        if current_participant:
            logout_user()
            session.clear()
            self.module.send_participant_disconnect_module_message(current_participant.participant_uuid)
            # Add token to disabled set
            if 'Authorization' in request.headers:
                scheme, old_token = request.headers['Authorization'].split(None, 1)
                if scheme == 'OpenTera':
                    # Only dynamic tokens
                    if old_token != current_participant.participant_token:
                        LoginModule.participant_add_disabled_token(old_token)

            return gettext("Participant logged out."), 200
        else:
            return gettext("Participant not logged in"), 403
