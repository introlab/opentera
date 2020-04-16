import datetime
from datetime import timedelta

from flask import jsonify, session, request
from flask_restx import Resource, reqparse, fields
from services.BureauActif.FlaskModule import default_api_ns as api

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('date', type=str, help='First day of the month for the data to query')


class QueryCalendarData(Resource):

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
        calendar_data = [
            {
                'date': (datetime.datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'seating': {
                    'remaining': 0.5,
                    'done': 5.5
                },
                'standing': {
                    'remaining': 3.00,
                    'done': 0.5
                },
                'positionChanges': {
                    'remaining': 8,
                    'done': 6
                }
            }, {
                'date': (datetime.datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d'),
                'seating': {
                    'remaining': 0.5,
                    'done': 4.5
                },
                'standing': {
                    'remaining': 1.5,
                    'done': 1.5
                },
                'positionChanges': {
                    'remaining': 5,
                    'done': 9
                }
            }, {
                'date': (datetime.datetime.today() - timedelta(days=5)).strftime('%Y-%m-%d'),
                'seating': {
                    'remaining': 1.5,
                    'done': 4.5
                },
                'standing': {
                    'remaining': 1.00,
                    'done': 2.5
                },
                'positionChanges': {
                    'remaining': 5,
                    'done': 9
                }
            }, {
                'date': (datetime.datetime.today() - timedelta(days=6)).strftime('%Y-%m-%d'),
                'seating': {
                    'remaining': 0,
                    'done': 3.5
                },
                'standing': {
                    'remaining': 0,
                    'done': 3.5
                },
                'positionChanges': {
                    'remaining': 0,
                    'done': 14
                }
            }, {
                'date': (datetime.datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'seating': {
                    'remaining': 0.5,
                    'done': 5.5
                },
                'standing': {
                    'remaining': 3.00,
                    'done': 0.5
                },
                'positionChanges': {
                    'remaining': 7,
                    'done': 7
                }
            }, {
                'date': (datetime.datetime.today() - timedelta(days=8)).strftime('%Y-%m-%d'),
                'seating': {
                    'remaining': 1.5,
                    'done': 4.5
                },
                'standing': {
                    'remaining': 2.5,
                    'done': 1.0
                },
                'positionChanges': {
                    'remaining': 8,
                    'done': 6
                }
            }, {
                'date': (datetime.datetime.today() - timedelta(days=11)).strftime('%Y-%m-%d'),
                'seating': {
                    'remaining': 1.0,
                    'done': 2.5
                },
                'standing': {
                    'remaining': 2.00,
                    'done': 1
                },
                'positionChanges': {
                    'remaining': 6,
                    'done': 8
                }
            }, {
                'date': (datetime.datetime.today() - timedelta(days=12)).strftime('%Y-%m-%d'),
                'seating': {
                    'remaining': 0.5,
                    'done': 3.0
                },
                'standing': {
                    'remaining': 1.00,
                    'done': 2.5
                },
                'positionChanges': {
                    'remaining': 4,
                    'done': 10
                }
            }, {
                'date': (datetime.datetime.today() - timedelta(days=13)).strftime('%Y-%m-%d'),
                'seating': {
                    'remaining': 0,
                    'done': 6.5
                },
                'standing': {
                    'remaining': 3,
                    'done': 0.5
                },
                'positionChanges': {
                    'remaining': 11,
                    'done': 1
                }
            }, {
                'date': (datetime.datetime.today() - timedelta(days=14)).strftime('%Y-%m-%d'),
                'seating': {
                    'remaining': 1.5,
                    'done': 4.5
                },
                'standing': {
                    'remaining': 2.5,
                    'done': 1.0
                },
                'positionChanges': {
                    'remaining': 8,
                    'done': 6
                }
            }
        ]

        data = []
        if not args['date']:
            return 'Missing date argument', 400
        elif args['date']:
            date = datetime.datetime.strptime(args['date'], '%Y-%m-%d').date()
            # TODO get data for the specified month

        return calendar_data, 200
