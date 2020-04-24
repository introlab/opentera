import datetime
from datetime import timedelta

from flask import jsonify, session, request
from flask_restx import Resource, reqparse, fields
from sqlalchemy.exc import InvalidRequestError
from services.BureauActif.FlaskModule import default_api_ns as api

from services.BureauActif.libbureauactif.db.DBManager import DBManager

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
        calendar_access = DBManager.calendarAccess()
        parser = get_parser

        args = parser.parse_args()

        calendar_days = []
        if not args['date']:
            return 'Missing date argument', 400
        elif args['date']:
            date = datetime.datetime.strptime(args['date'], '%d-%m-%Y').date()
            calendar_days = calendar_access.query_calendar_day_by_month(date)

        try:
            calendar_days_list = []
            if calendar_days is not None:
                for day in calendar_days:
                    if day is not None:
                        day_json = day.to_json()

                        day_json['seating'] = day.seating.to_json()
                        day_json['standing'] = day.standing.to_json()
                        day_json['positionChanges'] = day.positionChanges.to_json()

                        calendar_days_list.append(day_json)

            return jsonify(calendar_days_list)

        except InvalidRequestError:
            return '', 500
