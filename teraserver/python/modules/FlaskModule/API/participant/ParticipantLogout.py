from flask import jsonify, session
from flask_login import logout_user
from flask_restplus import Resource, reqparse, fields
from modules.LoginModule.LoginModule import participant_multi_auth
from modules.FlaskModule.FlaskModule import participant_api_ns as api


# Parser definition(s)
get_parser = api.parser()
post_parser = api.parser()


class ParticipantLogout(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @api.expect(get_parser)
    @api.doc(description='Logout participant',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        print('logout participant')
        logout_user()
        session.clear()
        return "Participant logged out.", 200

