from flask import jsonify, session
from flask_restplus import Resource, reqparse, fields
from modules.LoginModule.LoginModule import http_auth
from modules.FlaskModule.FlaskModule import participant_api_ns as api


# Parser definition(s)
get_parser = api.parser()
post_parser = api.parser()


class ParticipantQueryDevices(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @api.expect(get_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        return '', 501

    # Handle auth
    @api.expect(post_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def post(self):
        return '', 501
