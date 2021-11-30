import datetime

from flask import jsonify
from flask_restx import Resource, reqparse
from sqlalchemy.exc import InvalidRequestError

from services.BureauActif.FlaskModule import default_api_ns as api

from services.BureauActif.libbureauactif.db.DBManager import DBManager

from opentera.services.ServiceAccessManager import ServiceAccessManager, current_participant_client

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('date', type=str, help='Date of first day of six to query')
get_parser.add_argument('uuid', type=str, help='Uuid of the participant to query')


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
    @ServiceAccessManager.token_required()
    def get(self):
        timeline_access = DBManager.timelineAccess()
        parser = get_parser

        args = parser.parse_args()

        timeline_days = []
        if not args['date']:
            return 'Missing date argument', 400
        elif args['date']:
            date = datetime.datetime.strptime(args['date'], '%d-%m-%Y').date()
            if args['uuid']:
                participant_uuid = args['uuid']
            else:
                participant_uuid = current_participant_client.participant_uuid
            timeline_days = timeline_access.query_timeline_days(date, participant_uuid)

        try:
            timeline_days_list = []
            if timeline_days is not None:
                for day in timeline_days:
                    if day is not None and len(day.series) > 1:
                        day_json = day.to_json()

                        timeline_days_list.append(day_json)

            return jsonify(timeline_days_list)

        except InvalidRequestError:
            return '', 500
