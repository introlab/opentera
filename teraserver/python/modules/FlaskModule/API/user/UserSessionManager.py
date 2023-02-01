from flask import session, request
from flask_restx import Resource
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraSession import TeraSession
from flask_babel import gettext
from modules.DatabaseModule.DBManager import DBManager
from opentera.redis.RedisRPCClient import RedisRPCClient
import json

# Parser definition(s)
post_parser = api.parser()
post_parser.add_argument('session_manage', type=str, location='json', help='Informations to manage the session',
                         required=True)
post_parser.add_argument('token', type=str, help='Secret Token')

session_manager_schema = api.schema_model('session_manage', {
    'properties': {
        'session_manage': {
            'type': 'object',
            'properties': {
                'session_uuid': {
                    'type': 'str'
                },
                'id_service': {
                    'type': 'integer'
                },
                'id_session': {
                    'type': 'integer'
                },
                'id_creator_user': {
                    'type': 'integer'
                },
                'id_session_type': {
                    'type': 'integer'
                },
                'session_participants': {
                    'type': 'array',
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'format': 'uuid'
                    }
                },
                'session_users': {
                    'type': 'array',
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'format': 'uuid'
                    }
                },
                'session_devices': {
                    'type': 'array',
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'format': 'uuid'
                    }
                },
                'action': {
                    'type': 'string'  # 'start', 'stop', 'invite', 'remove', 'invite_reply'
                },
                'parameters': {  # For invite_reply, parameter must contains 'reply_code' and 'reply_msg'. 'reply_code'
                                 # can either be a direct int value from JoinSessionReplyEvent or a string with one of
                                 # those value: 'accept', 'reject', 'busy', 'timeout'
                    'type': 'object'
                }
            },
            'required': ['action']
        },

    },
    'type': 'object',
    'required': ['session_manage']
})


class UserSessionManager(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Manage a specific session',
             responses={200: 'Success',
                        400: 'Required parameter is missing',
                        500: 'Internal server error',
                        501: 'Not implemented',
                        403: 'Logged user doesn\'t have enough permission'})
    @api.expect(post_parser)
    @api.expect(session_manager_schema)
    @user_multi_auth.login_required
    def post(self):
        args = post_parser.parse_args()
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        if 'session_manage' not in request.json:
            return '', 400

        json_session_manager = request.json['session_manage']

        if 'action' not in json_session_manager:
            return gettext('Missing action', 400)

        # if 'id_service' not in json_session_manager:
        #     return gettext('Missing service id'), 400

        if 'id_creator_user' not in json_session_manager:
            json_session_manager['id_creator_user'] = current_user.id_user

        current_session = None
        if 'id_session' not in json_session_manager:
            if 'session_uuid' in json_session_manager:
                # Get session id for uuid
                current_session = TeraSession.get_session_by_uuid(json_session_manager['session_uuid'])
                if not current_session:
                    return gettext('Invalid session'), 400
                json_session_manager['id_session'] = current_session.id_session
            else:
                json_session_manager['id_session'] = 0

        if json_session_manager['id_session'] != 0:
            ses = user_access.query_session(json_session_manager['id_session'])
            if not ses:
                return gettext('User doesn\'t have access to that session'), 403

            if not current_session:
                current_session = TeraSession.get_session_by_id(json_session_manager['id_session'])
            if not current_session:
                return gettext('Invalid session'), 400

            if 'id_service' not in json_session_manager:
                # Check if there's a service for that session, and, if so, adds its id.
                if current_session.session_session_type.id_service:
                    json_session_manager['id_service'] = current_session.session_session_type.id_service
            if 'id_session_type' not in json_session_manager:
                json_session_manager['id_session_type'] = current_session.id_session_type

            # Compare session users, participants, devices...
            if 'session_users' not in json_session_manager:
                json_session_manager['session_users'] = [user.user_uuid for user in current_session.session_users]
            if 'session_participants' not in json_session_manager:
                json_session_manager['session_participants'] = [part.participant_uuid
                                                                for part in current_session.session_participants]
            if 'session_devices' not in json_session_manager:
                json_session_manager['session_devices'] = [device.device_uuid
                                                           for device in current_session.session_devices]
        else:
            # New session - require session type
            if 'id_session_type' not in json_session_manager:
                return gettext('Missing required id_session_type for new sessions'), 400

        # Validate user rights if user can access that service
        if 'id_service' in json_session_manager:
            if json_session_manager['id_service'] not in user_access.get_accessible_services_ids():
                return gettext('User doesn\'t have access to that service.'), 403

        # Validate that we have the correct parameters for invite_reply
        if json_session_manager['action'] == 'invite_reply':
            if 'parameters' not in json_session_manager:
                return gettext('Missing parameters'), 400
            parameters = json_session_manager['parameters']
            if 'reply_code' not in parameters:
                return gettext('Missing reply code in parameters'), 400
            # Validate reply code, based on JoinSessionReplyEvent enum
            from opentera.messages.python.JoinSessionReplyEvent_pb2 import JoinSessionReplyEvent
            if isinstance(parameters['reply_code'], str):
                if parameters['reply_code'] == 'accept':
                    parameters['reply_code'] = JoinSessionReplyEvent.REPLY_ACCEPTED
                elif parameters['reply_code'] == 'reject' or parameters['reply_code'] == 'deny':
                    parameters['reply_code'] = JoinSessionReplyEvent.REPLY_DENIED
                elif parameters['reply_code'] == 'busy':
                    parameters['reply_code'] = JoinSessionReplyEvent.REPLY_BUSY
                elif parameters['reply_code'] == 'timeout':
                    parameters['reply_code'] = JoinSessionReplyEvent.REPLY_TIMEOUT
                else:
                    return gettext('Invalid reply code'), 400
            elif isinstance(parameters['reply_code'], int):
                if parameters['reply_code'] > JoinSessionReplyEvent.REPLY_TIMEOUT or parameters['reply_code'] < 1:
                    return gettext('Invalid reply code'), 400
            parameters['user_uuid'] = current_user.user_uuid

        answer = None

        if 'id_service' in json_session_manager:
            service = TeraService.get_service_by_id(json_session_manager['id_service'])
            if not service:
                return gettext('Service not found'), 400
            rpc = RedisRPCClient(self.module.config.redis_config)
            answer = rpc.call_service(service.service_key, 'session_manage', json.dumps(request.json))
        else:
            # TODO: Manage other session types
            return gettext('Not implemented yet'), 501

        # TODO If session is of category "Service":
        # - Starts / stops / ... the service using RPC API:
        #       * User roles for that service and project
        #       * id_session if exists
        #       * Action to do
        #       * Users / participants list
        # - Service will create session if needed or reuse existing one
        # - Service will send invitations / updates to participants / users
        # - Service will return id_session and status code as a result to the RPC call and this will be the reply of
        #   this query
        if answer:
            # MANAGED IN SERVICES
            return answer, 200
        else:
            return gettext('No answer from service.'), 500



