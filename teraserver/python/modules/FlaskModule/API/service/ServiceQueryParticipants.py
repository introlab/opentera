from flask import jsonify, session
from flask_restplus import Resource, reqparse, fields, inputs
from modules.LoginModule.LoginModule import LoginModule
from modules.FlaskModule.FlaskModule import service_api_ns as api
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
post_parser = api.parser()


class ServiceQueryParticipants(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return participant information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        print('hello')
        return 'Not implemented', 501

    @LoginModule.service_token_or_certificate_required
    @api.expect(post_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def post(self):
        print('hello')
        return 'Not Implemented', 501
