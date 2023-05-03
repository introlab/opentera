import datetime

from flask_restx import Resource, inputs
from sqlalchemy.exc import InvalidRequestError
from services.LoggingService.FlaskModule import logging_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_user_client
from services.LoggingService.libloggingservice.db.models.LogEntry import LogEntry
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('limit', type=int, help='Maximum number of results to return', default=None)
get_parser.add_argument('offset', type=int, help='Number of items to ignore in results, offset from 0-index',
                        default=None)
get_parser.add_argument('start_date', type=inputs.datetime_from_iso8601,
                        help='Start date, sessions before that date will be ignored', default=None)
get_parser.add_argument('end_date', type=inputs.datetime_from_iso8601,
                        help='End date, sessions after that date will be ignored', default=None)
get_parser.add_argument('stats', type=inputs.boolean, help='Only query stats about the logs', default=False)
get_parser.add_argument('log_level', type=int, help='Minimum log level to retrieve', default=None)


class QueryLogEntries(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.expect(get_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @ServiceAccessManager.token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    @ServiceAccessManager.service_user_roles_required(['admin'])
    def get(self):
        args = get_parser.parse_args()
        # Access to logs is restricted to admin roles and superadmins
        # Verified in ServiceAccessManager.service_user_roles_required
        if current_user_client:
            try:
                query = LogEntry.query

                # Handle query parameters
                if args['log_level']:
                    query = query.filter(LogEntry.log_level == args['log_level'])

                if args['start_date']:
                    query = query.filter(LogEntry.timestamp >= args['start_date'])
                if args['end_date']:
                    query = query.filter(LogEntry.timestamp <= args['end_date'])

                if not args['stats']:
                    query = query.order_by(LogEntry.timestamp.desc())

                    # Must be applied after filter
                    if args['limit']:
                        query = query.limit(args['limit'])
                    if args['offset']:
                        query = query.offset(args['offset'])

                    all_entries = query.all()
                    results = []
                    for entry in all_entries:
                        results.append(entry.to_json(minimal=False))
                    return results
                else:
                    count = query.count()
                    min_max_dates = query.with_entities(LogEntry.db().func.min(LogEntry.timestamp),
                                                        LogEntry.db().func.max(LogEntry.timestamp)).first()
                    rval = {'count': count,
                            'min_timestamp':
                                min_max_dates[0].isoformat()
                                if min_max_dates[0] else datetime.datetime.now().isoformat(),
                            'max_timestamp': min_max_dates[1].isoformat()
                            if min_max_dates[1] else datetime.datetime.now().isoformat()
                            }
                    return rval
            except InvalidRequestError as e:
                return gettext('Database error: ') + str(e), 500

        return 'Unauthorized', 403
