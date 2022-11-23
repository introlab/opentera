from sqlalchemy.exc import InvalidRequestError
from services.LoggingService.FlaskModule import logging_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_user_client, \
    current_participant_client, current_device_client
from services.LoggingService.libloggingservice.db.models.LoginEntry import LoginEntry
import services.LoggingService.Globals as Globals
from flask_restx import Resource, inputs
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('limit', type=int, help='Maximum number of results to return', default=None)
get_parser.add_argument('offset', type=int, help='Number of items to ignore in results, offset from 0-index',
                        default=None)
get_parser.add_argument('start_date', type=inputs.datetime_from_iso8601,
                        help='Start date, sessions before that date will be ignored', default=None)
get_parser.add_argument('end_date', type=inputs.datetime_from_iso8601,
                        help='End date, sessions after that date will be ignored', default=None)
get_parser.add_argument('user_uuid', type=str, help='filter results for this user_uuid', default=None)
get_parser.add_argument('participant_uuid', type=str, help='filter results for this participant_uuid', default=None)
get_parser.add_argument('device_uuid', type=str, help='filter results for this device_uuid', default=None)
get_parser.add_argument('stats', type=inputs.boolean, help='Only query stats about the logs', default=False)
get_parser.add_argument('log_level', type=int, help='Minimum log level to retrieve', default=None)


class QueryLoginEntries(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.expect(get_parser)
    @api.doc(description='Query all login entries ',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @ServiceAccessManager.token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def get(self):

        args = get_parser.parse_args()

        # Request access from server params will depend on a user, participant or device
        params = {
            'from_user_uuid': current_user_client.user_uuid if current_user_client else None,
            'from_participant_uuid': current_participant_client.participant_uuid if current_participant_client else None,
            'from_device_uuid': current_device_client.device_uuid if current_device_client else None,
            'with_users_uuids': True,
            'with_projects_ids': True,
            'with_participants_uuids': True,
            'with_devices_uuids': True,
            'with_sites_ids': True,
            'admin': False
        }

        response = Globals.service.get_from_opentera('/api/service/access', params)
        if response.status_code == 200:
            # Response should include ourselves (user, participant or device)
            users_uuids = response.json['users_uuids']
            participants_uuids = response.json['participants_uuids']
            devices_uuids = response.json['devices_uuids']
            # TODO not used for now...
            # projects_ids = response.json['projects_ids']
            # sites_ids = response.json['sites_ids']

            try:
                all_entries = []
                results = []

                # Update uuids for specific requests
                # Doing list intersection with requested uuids and accessible uuids
                if args['user_uuid']:
                    users_uuids = [args['user_uuid']] if args['user_uuid'] in users_uuids else []

                if args['participant_uuid']:
                    participants_uuids = [args['participant_uuid']] \
                        if args['participant_uuid'] in participants_uuids else []

                if args['device_uuid']:
                    devices_uuids = [args['device_uuid']] \
                        if args['device_uuid'] in devices_uuids else []

                # Base query will order desc from most recent to last recent
                query = LoginEntry.query

                # Handle query parameters
                if args['log_level']:
                    query = query.filter(LoginEntry.login_log_level <= args['log_level'])

                if args['start_date']:
                    query = query.filter(LoginEntry.login_timestamp >= args['start_date'])
                if args['end_date']:
                    query = query.filter(LoginEntry.login_timestamp <= args['end_date'])

                if not current_user_client or (current_user_client and current_user_client.user_superadmin is False) \
                        or args['user_uuid'] or args['participant_uuid'] or args['device_uuid']:
                    # Filter according to access only for other than super admins unless specific uuids are requested.
                    query = query.filter(
                        LoginEntry.login_user_uuid.in_(users_uuids) |
                        LoginEntry.login_participant_uuid.in_(participants_uuids) |
                        LoginEntry.login_device_uuid.in_(devices_uuids))

                if not args['stats']:

                    query = query.order_by(LoginEntry.login_timestamp.desc())

                    # Must be applied after filter
                    if args['limit']:
                        query = query.limit(args['limit'])
                    if args['offset']:
                        query = query.offset(args['offset'])

                    all_entries.extend(query.all())

                    # Return json result
                    for entry in all_entries:
                        results.append(entry.to_json(minimal=False))
                    return results
                else:
                    count = query.count()
                    min_max_dates = query.with_entities(LoginEntry.db().func.min(LoginEntry.login_timestamp),
                                                        LoginEntry.db().func.max(LoginEntry.login_timestamp)).first()

                    result = {'count': count,
                              'min_timestamp': min_max_dates[0].isoformat(),
                              'max_timestamp': min_max_dates[1].isoformat(),
                              }
                    return result

            except InvalidRequestError as e:
                gettext('Database error: ') + str(e), 500

        else:
            return 'Unauthorized', 403
