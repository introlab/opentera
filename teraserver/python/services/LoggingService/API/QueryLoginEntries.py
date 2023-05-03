import datetime

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import or_
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
get_parser.add_argument('with_names', type=inputs.boolean, help='Also includes associated names with uuids / ids',
                        default=False)


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
    @ServiceAccessManager.service_user_roles_required(['admin'])
    def get(self):

        args = get_parser.parse_args()

        # Request access from server params will depend on a user, participant or device
        params = {
            'from_user_uuid': current_user_client.user_uuid if current_user_client else None,
            'from_participant_uuid':
                current_participant_client.participant_uuid if current_participant_client else None,
            'from_device_uuid': current_device_client.device_uuid if current_device_client else None,
            'with_users': True,
            'with_projects': False,
            'with_participants': True,
            'with_devices': True,
            'with_sites': False,
            'admin': False,
            'with_names': args['with_names']
        }

        response = Globals.service.get_from_opentera('/api/service/access', params)
        if response.status_code == 200:
            import json
            response_json = json.loads(response.text)
            # Response should include ourselves (user, participant or device)
            users = response_json['users']
            participants = response_json['participants']
            devices = response_json['devices']
            # TODO not used for now...
            # projects_ids = response.json['projects_ids']
            # sites_ids = response.json['sites_ids']

            try:
                all_entries = []
                results = []
                users_uuids = [params['from_user_uuid']]
                participants_uuids = [params['from_participant_uuid']]
                devices_uuids = [params['from_device_uuid']]

                # Update uuids for specific requests
                # Doing list intersection with requested uuids and accessible uuids
                if args['user_uuid']:
                    users_uuids = [args['user_uuid']] if args['user_uuid'] in [user['uuid'] for user in users] else []

                if args['participant_uuid']:
                    participants_uuids = [args['participant_uuid']] \
                        if args['participant_uuid'] in [part['uuid'] for part in participants] else []

                if args['device_uuid']:
                    devices_uuids = [args['device_uuid']] \
                        if args['device_uuid'] in [device['uuid'] for device in devices] else []

                # Base query will order desc from most recent to last recent
                query = LoginEntry.query

                # Handle query parameters
                if args['log_level']:
                    query = query.filter(LoginEntry.login_log_level == args['log_level'])

                if args['start_date']:
                    query = query.filter(LoginEntry.login_timestamp >= args['start_date'])
                if args['end_date']:
                    query = query.filter(LoginEntry.login_timestamp <= args['end_date'])

                if not current_user_client or (current_user_client and current_user_client.user_superadmin is False)\
                        or args['user_uuid'] or args['participant_uuid'] or args['device_uuid']:
                    # Filter according to access only for other than super admins unless specific uuids are requested.
                    login_filter = []
                    if args['user_uuid']:
                        login_filter.append(LoginEntry.login_user_uuid.in_(users_uuids))

                    if args['participant_uuid'] or current_participant_client:
                        login_filter.append(LoginEntry.login_participant_uuid.in_(participants_uuids))

                    if args['device_uuid'] or current_device_client:
                        login_filter.append(LoginEntry.login_device_uuid.in_(devices_uuids))
                    query = query.filter(or_(*login_filter))

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
                        result = entry.to_json(minimal=False)

                        if args['with_names']:
                            # Also append the name of the associated element
                            result['login_user_name'] = next((user['name'] for user in users
                                                              if user['uuid'] == entry.login_user_uuid), None)
                            result['login_participant_name'] = next((part['name'] for part in participants
                                                                     if part['uuid'] == entry.login_participant_uuid),
                                                                    None)
                            result['login_device_name'] = next((device['name'] for device in devices
                                                                if device['uuid'] == entry.login_device_uuid), None)

                        results.append(result)
                    return results
                else:
                    count = query.count()
                    min_max_dates = query.with_entities(LoginEntry.db().func.min(LoginEntry.login_timestamp),
                                                        LoginEntry.db().func.max(LoginEntry.login_timestamp)).first()
                    result = {'count': count,
                              'min_timestamp': min_max_dates[0].isoformat()
                              if min_max_dates[0] else datetime.datetime.now().isoformat(),
                              'max_timestamp': min_max_dates[1].isoformat()
                              if min_max_dates[1] else datetime.datetime.now().isoformat()
                              }
                    return result

            except InvalidRequestError as e:
                gettext('Database error: ') + str(e), 500

        else:
            return 'Unauthorized', 403
