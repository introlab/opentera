from flask import request
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraSession import TeraSession
from opentera.redis.RedisVars import RedisVars
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy import exc
from datetime import datetime


# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_test', type=int, help='Specific ID of test to query information.')
get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all tests')
get_parser.add_argument('id_session', type=int, help='ID of session from which to request all tests')
get_parser.add_argument('id_participant', type=int, help='ID of participant from which to request all tests')
get_parser.add_argument('id_user', type=int, help='ID of the user from which to request all tests.')
get_parser.add_argument('service_uuid', type=str, help='Query all tests associated with that service uuid')

get_parser.add_argument('with_urls', type=inputs.boolean, help='Also include tests infos and download-upload url')
get_parser.add_argument('with_only_token', type=inputs.boolean, help='Only includes the access token. '
                                                                     'Will ignore with_urls if specified.')

post_parser = api.parser()

delete_parser = api.parser()
delete_parser.add_argument('uuid', type=str, help='Test UUID to delete', required=True)


class ServiceQueryTests(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return tests information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged service doesn\'t have permission to access the requested data'})
    def get(self):
        service_access = DBManager.serviceAccess(current_service)

        args = get_parser.parse_args()

        # If we have no arguments, don't do anything!
        tests = []
        if not any(args.values()):
            return gettext('No arguments specified'), 400
        elif args['id_device']:
            if args['id_device'] not in service_access.get_accessible_devices_ids():
                return gettext('Device access denied'), 403
            tests = TeraTest.get_tests_for_device(device_id=args['id_device'])
        elif args['id_session']:
            if args['id_session'] not in service_access.get_accessible_sessions_ids():
                return gettext('Session access denied'), 403
            tests = TeraTest.get_tests_for_session(session_id=args['id_session'])
        elif args['id_participant']:
            if args['id_participant'] not in service_access.get_accessible_participants_ids():
                return gettext('Participant access denied'), 403
            tests = TeraTest.get_tests_for_participant(part_id=args['id_participant'])
        elif args['id_user']:
            if args['id_user'] not in service_access.get_accessible_users_ids():
                return gettext("User access denied"), 403
            tests = TeraTest.get_tests_for_user(user_id=args['id_user'])
        elif args['id_test']:
            tests = [service_access.query_test(args['id_test'])]
        elif args['service_uuid']:
            service = TeraService.get_service_by_uuid(args['service_uuid'])
            tests = TeraTest.get_tests_for_service(service_id=service.id_service)
        else:
            return gettext('Missing argument'), 400

        tests_list = []
        access_token = None
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        if not tests:
            tests = []

        for test in tests:
            if not test:
                continue
            if args['with_only_token']:
                test_json = {'test_uuid': test.test_uuid}
            else:
                test_json = test.to_json()

            # Access token
            if args['with_urls'] or args['with_only_token']:
                # Access token
                token_key = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
                access_token = TeraTest.get_access_token(test_uuids=test.test_uuid,
                                                         token_key=token_key,
                                                         requester_uuid=current_service.service_uuid,
                                                         expiration=1800)
                test_json['access_token'] = access_token
            if args['with_urls']:
                test_json.update(test.get_service_url(server_url=servername, server_port=port))
            tests_list.append(test_json)

        return tests_list

    @LoginModule.service_token_or_certificate_required
    # @api.expect(post_parser)
    @api.doc(description='Adds a new test to the OpenTera database',
             responses={200: 'Success - test correctly added',
                        400: 'Bad request - wrong or missing parameters in query',
                        500: 'Required parameter is missing',
                        403: 'Service doesn\'t have permission to post that test'})
    def post(self):
        service_access = DBManager.serviceAccess(current_service)

        # Using request.json instead of parser, since parser messes up the json!
        if 'test' not in request.json:
            return gettext('Missing test field'), 400

        test_info = request.json['test']

        # All fields validation
        if 'id_test' not in test_info:
            return gettext('Missing id_test field'), 400

        if test_info['id_test'] == 0:
            if 'id_session' not in test_info and 'session_uuid' not in test_info:
                return gettext('Unknown session'), 400

            if 'session_uuid' in test_info and 'id_session' not in test_info:
                # Get session id
                target_session = TeraSession.get_session_by_uuid(test_info['session_uuid'])
                if not target_session:
                    return gettext('Unknown session'), 400
                test_info['id_session'] = target_session.id_session

            if 'session_uuid' in test_info:
                del test_info['session_uuid']

            if 'id_test_type' not in test_info and 'test_type_uuid' not in test_info:
                return gettext('Missing id_test_type field'), 400

            if 'test_type_uuid' in test_info:
                test_type = TeraTestType.get_test_type_by_uuid(test_info['test_type_uuid'])
                if not test_type:
                    return gettext('Invalid test type'), 400
                test_info.pop('test_type_uuid')
                test_info['id_test_type'] = test_type.id_test_type
            else:
                test_type = TeraTestType.get_test_type_by_id(test_info['id_test_type'])

            if 'test_datetime' not in test_info:
                test_info['test_datetime'] = datetime.now()

            if 'test_name' not in test_info:
                test_date = test_info['test_datetime']
                if not isinstance(test_date, datetime):
                    test_date = datetime.fromisoformat(test_info['test_datetime'])
                if test_type.test_type_key:
                    test_name = test_type.test_type_key
                else:
                    test_name = test_type.test_name
                test_name += ' #' + \
                             str(TeraTest.count_with_filters({'id_session': test_info['id_session'],
                                                              'id_test_type': test_info['id_test_type']})+1)
                test_info['test_name'] = test_name

        # Check if the service can create/update that test
        if test_info['id_test'] != 0 and 'id_session' not in test_info:
            # Updating asset - get asset and validate session asset
            test = TeraTest.get_test_by_id(test_info['id_test'])
            if test:
                test_info['id_session'] = test.id_session

        if test_info['id_session'] not in service_access.get_accessible_sessions_ids(True):
            return gettext('Service can\'t create tests for that session'), 403

        # Replace creator uuids with ids if required
        if 'participant_uuid' in test_info:
            from opentera.db.models.TeraParticipant import TeraParticipant
            part = TeraParticipant.get_participant_by_uuid(test_info['participant_uuid'])
            if not part:
                return gettext('Invalid participant'), 400
            test_info.pop('participant_uuid')
            test_info['id_participant'] = part.id_participant

        if 'user_uuid' in test_info:
            from opentera.db.models.TeraUser import TeraUser
            user = TeraUser.get_user_by_uuid(test_info['user_uuid'])
            if not user:
                return gettext('Invalid user'), 400
            test_info.pop('user_uuid')
            test_info['id_user'] = user.id_user

        if 'device_uuid' in test_info:
            from opentera.db.models.TeraDevice import TeraDevice
            device = TeraDevice.get_device_by_uuid(test_info['device_uuid'])
            if not device:
                return gettext('Invalid device'), 400
            test_info.pop('device_uuid')
            test_info['id_device'] = device.id_device

        # Create a new test?
        if test_info['id_test'] == 0:
            try:
                # Create asset
                new_test = TeraTest()
                new_test.from_json(test_info)
                TeraTest.insert(new_test)
                # Update ID for further use
                test_info['id_test'] = new_test.id_test
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryTests.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # Update test
            try:
                TeraTest.update(test_info['id_test'], test_info)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryTests.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        update_test = TeraTest.get_test_by_id(test_info['id_test'])

        return [update_test.to_json()]

    @LoginModule.service_token_or_certificate_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific test',
             responses={200: 'Success',
                        403: 'Service can\'t delete test',
                        500: 'Database error.'})
    def delete(self):
        service_access = DBManager.serviceAccess(current_service)
        parser = delete_parser

        args = parser.parse_args()
        uuid_todel = args['uuid']

        test = TeraTest.get_test_by_uuid(uuid_todel)

        if not test:
            return gettext('Missing arguments'), 400

        if test.id_session not in service_access.get_accessible_sessions_ids(True):
            return gettext('Service can\'t delete tests for that session'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraTest.delete(id_todel=test.id_test)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryTests.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200

