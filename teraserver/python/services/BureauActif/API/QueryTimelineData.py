import datetime

from flask import jsonify, session, request
from flask_restx import Resource, reqparse, fields
from services.BureauActif.FlaskModule import default_api_ns as api

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('date', type=datetime, help='Date of first day of six to query')


class QueryTimelineData(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.parser = reqparse.RequestParser()

    @api.expect(get_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        parser = get_parser

        args = parser.parse_args()

        data = []
        if not args['date']:
            today = datetime.datetime.now()
            # TODO get data for present month
        elif args['date']:
            today = datetime.datetime.now()
            # TODO get data for the specified month

        return today.isoformat(), 200
