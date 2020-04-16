import datetime

from flask import jsonify, session, request
from flask_restx import Resource, reqparse, fields
from services.BureauActif.FlaskModule import default_api_ns as api

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('date', type=str, help='Date of first day of six to query')


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
        timeline_data = [
            {
                'name': '02-03-2020',
                'series': [
                    {
                        'value': 7.8,
                        'name': ' '
                    },
                    {
                        'value': 0.5,
                        'name': 'Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.1,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.02,
                        'name': 'Absent'
                    },
                    {
                        'value': 0.4,
                        'name': 'Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Assis'
                    },
                    {
                        'value': 0.4,
                        'name': 'Debout'
                    },
                    {
                        'value': 0.1,
                        'name': 'Absent'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.4,
                        'name': 'Debout'
                    },
                    {
                        'value': 0.1,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                ]
            },
            {
                'name': '03-03-2020',
                'series': [
                    {
                        'value': 8,
                        'name': ' '
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Debout'
                    },
                    {
                        'value': 0.2,
                        'name': 'Absent'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.87,
                        'name': 'Absent'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                ]
            },
            {
                'name': '04-03-2020',
                'series': [
                    {
                        'value': 7.45,
                        'name': ' '
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.1,
                        'name': 'Debout'
                    },
                    {
                        'value': 0.4,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.7,
                        'name': 'Absent'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.3,
                        'name': 'Debout'
                    },
                    {
                        'value': 0.2,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.5,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.5,
                        'name': 'Bouton appuyé - Debout'
                    },
                    {
                        'value': 0.2,
                        'name': 'Assis'
                    },
                    {
                        'value': 0.2,
                        'name': 'Absent'
                    },
                    {
                        'value': 0.3,
                        'name': 'Assis'
                    },
                ]
            }
        ]

        data = []
        if not args['date']:
            return 'Missing date argument', 400
        elif args['date']:
            date = datetime.datetime.strptime(args['date'], '%Y-%m-%d').date()
            # TODO get data for the specified date + 6 days

        return timeline_data, 200
