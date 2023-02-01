from flask import session, request
from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraTest import TeraTest
from sqlalchemy import exc

from modules.DatabaseModule.DBManager import DBManager
from opentera.redis.RedisVars import RedisVars

# Parser definition(s)
# GET
get_parser = api.parser()
get_parser.add_argument('id_test', type=int, help='Specific ID of test to query information.')
get_parser.add_argument('test_uuid', type=str, help='Specific UUID of test to query information.')
get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all tests')
get_parser.add_argument('id_session', type=int, help='ID of session from which to request all tests')
get_parser.add_argument('id_participant', type=int, help='ID of participant from which to request all tests')
get_parser.add_argument('id_user', type=int, help='ID of the user from which to request all tests.')

get_parser.add_argument('with_urls', type=inputs.boolean, help='Also include tests results url')
get_parser.add_argument('with_only_token', type=inputs.boolean, help='Only includes the access token. '
                                                                     'Will ignore with_urls if specified.')
get_parser.add_argument('full', type=inputs.boolean, help='Also include names of sessions, users, services, ... in the '
                                                          'reply')
get_parser.add_argument('token', type=str, help='Secret Token')

post_parser = api.parser()
post_parser.add_argument('token', type=str, help='Secret Token')

delete_parser = api.parser()
delete_parser.add_argument('id', type=int, help='Test type ID to delete', required=True)
delete_parser.add_argument('token', type=str, help='Secret Token')


class UserQueryTests(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get test information. Only one of the ID parameter is supported at once',
             responses={200: 'Success - returns list of assets',
                        400: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

        # At least one argument required
        if not any(args.values()):
            return gettext('No arguments specified'), 400
        elif args['id_device']:
            if args['id_device'] not in user_access.get_accessible_devices_ids():
                return gettext('Device access denied'), 403
            tests = TeraTest.get_tests_for_device(device_id=args['id_device'])
        elif args['id_session']:
            if not user_access.query_session(session_id=args['id_session']):
                return gettext('Session access denied'), 403
            tests = TeraTest.get_tests_for_session(session_id=args['id_session'])
        elif args['id_participant']:
            if args['id_participant'] not in user_access.get_accessible_participants_ids():
                return gettext('Participant access denied'), 403
            tests = TeraTest.get_tests_for_participant(part_id=args['id_participant'])
        elif args['id_user']:
            if args['id_user'] not in user_access.get_accessible_users_ids():
                return gettext("User access denied"), 403
            tests = TeraTest.get_tests_for_user(user_id=args['id_user'])
        elif args['id_test']:
            tests = [user_access.query_test(test_id=args['id_test'])]
        elif args['test_uuid']:
            tests = [user_access.query_test(test_uuid=args['test_uuid'])]
        else:
            return gettext('Missing argument'), 400

        if not tests:
            return []

        tests_list = []
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        for test in tests:
            if test is None:
                continue

            if args['with_only_token']:
                test_json = {'test_uuid': test.test_uuid}
            else:
                test_json = test.to_json(minimal=not args['full'])

            # Access token
            if args['with_urls'] or args['with_only_token']:
                # Access token
                token_key = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
                access_token = TeraTest.get_access_token(test_uuids=test.test_uuid,
                                                         token_key=token_key,
                                                         requester_uuid=current_user.user_uuid,
                                                         expiration=1800)
                test_json['access_token'] = access_token

            if args['with_urls']:
                # We have previously verified that the service is available to the user
                test_json.update(test.get_service_url(server_url=servername, server_port=port))

            tests_list.append(test_json)

        return tests_list

    @api.doc(description='Delete test.',
             responses={501: 'Unable to update test from here - use service!'})
    @api.expect(post_parser)
    @user_multi_auth.login_required
    def post(self):
        return gettext('Test information update and creation must be done directly into a service (such as '
                       'Test service)'), 501

    @api.doc(description='Delete a specific test',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete test',
                        500: 'Database error.'})
    @api.expect(delete_parser)
    @user_multi_auth.login_required
    def delete(self):
        user_access = DBManager.userAccess(current_user)
        args = delete_parser.parse_args(strict=True)
        id_todel = args['id']

        # Check if current user can delete
        if not user_access.query_test(id_todel):
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraTest.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryTests.__name__,
                                         'delete', 500, 'Database error', e)
            return gettext('Database error'), 500

        return '', 200
