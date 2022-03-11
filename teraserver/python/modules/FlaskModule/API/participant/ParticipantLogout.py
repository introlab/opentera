from flask import jsonify, session
from flask_login import logout_user
from flask_restx import Resource, reqparse, fields
from flask_babel import gettext
from modules.LoginModule.LoginModule import participant_multi_auth
from modules.FlaskModule.FlaskModule import participant_api_ns as api


# Parser definition(s)
get_parser = api.parser()
post_parser = api.parser()


class ParticipantLogout(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.expect(get_parser)
    @api.doc(description='Logout participant',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        print('logout participant')
        logout_user()
        session.clear()
        return gettext("Participant logged out."), 200

