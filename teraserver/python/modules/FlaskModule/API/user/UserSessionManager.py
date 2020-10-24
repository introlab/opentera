from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraService import TeraService
from libtera.db.models.TeraSession import TeraSession
from modules.RedisVars import RedisVars
from libtera.redis.RedisClient import RedisClient
from modules.BaseModule import ModuleNames, create_module_message_topic_from_name
import messages.python as messages
from flask_babel import gettext
from modules.DatabaseModule.DBManager import DBManager
from libtera.redis.RedisRPCClient import RedisRPCClient
import json

# Parser definition(s)
post_parser = api.parser()
post_parser.add_argument('session_manage', type=str, location='json', help='Informations to manage the session',
                         required=True)

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

    @user_multi_auth.login_required
    @api.expect(session_manager_schema)
    @api.doc(description='Manage a specific session',
             responses={200: 'Success',
                        400: 'Required parameter is missing',
                        500: 'Internal server error',
                        501: 'Not implemented',
                        403: 'Logged user doesn\'t have enough permission'})
    def post(self):
        args = post_parser.parse_args()

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])

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
            if 'id_service' not in json_session_manager:
                # Check if there's a service for that session, and, if so, adds its id.
                if not current_session:
                    current_session = TeraSession.get_session_by_id(json_session_manager['id_session'])
                if not current_session:
                    return gettext('Invalid session'), 400
                if current_session.session_session_type.id_service:
                    json_session_manager['id_service'] = current_session.session_session_type.id_service

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
            from messages.python.JoinSessionReplyEvent_pb2 import JoinSessionReplyEvent
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
            # Update UserManager module
            # MANAGED IN SERVICES
            # if 'session' in answer:
            #     if 'session_uuid' in answer['session']:
            #         session_uuid = answer['session']['session_uuid']
            #
            #         dest_topic_name = create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME)
            #         tera_message = self.module.create_tera_message(dest=dest_topic_name)
            #         if json_session_manager['action'] == 'start' or json_session_manager['action'] == 'invite':
            #             join_session_msg = messages.JoinSessionEvent()
            #             join_session_msg.session_uuid = session_uuid
            #             join_session_msg.session_users.extend(answer['session']['session_users'])
            #             join_session_msg.session_participants.extend(answer['session']['session_participants'])
            #             join_session_msg.session_devices.extend(answer['session']['session_devices'])
            #             any_message = messages.Any()
            #             any_message.Pack(join_session_msg)
            #             tera_message.data.extend([any_message])
            #             self.module.publish(dest_topic_name, tera_message.SerializeToString())
            #
            #         if json_session_manager['action'] == 'stop':
            #             stop_session_msg = messages.StopSessionEvent()
            #             stop_session_msg.session_uuid = session_uuid
            #             any_message = messages.Any()
            #             any_message.Pack(stop_session_msg)
            #             tera_message.data.extend([any_message])
            #             self.module.publish(dest_topic_name, tera_message.SerializeToString())
            #
            #         if json_session_manager['action'] == 'remove':
            #             leave_session_msg = messages.LeaveSessionEvent()
            #             leave_session_msg.session_uuid = session_uuid
            #             if 'session_users' in json_session_manager:
            #                 leave_session_msg.leaving_users.extend(json_session_manager['session_users'])
            #             if 'session_participants' in json_session_manager:
            #                 leave_session_msg.leaving_participants.extend(json_session_manager['session_participants'])
            #             if 'session_devices' in json_session_manager:
            #                 leave_session_msg.leaving_devices.extend(json_session_manager['session_devices'])
            #             any_message = messages.Any()
            #             any_message.Pack(leave_session_msg)
            #             tera_message.data.extend([any_message])
            #             self.module.publish(dest_topic_name, tera_message.SerializeToString())

            return answer, 200
        else:
            # Test and debug for now
            # if json_session_manager['action'] == 'start':
            #     return {'status': 'started', 'id_session': 1}, 200
            # if json_session_manager['action'] == 'stop':
            #     return {'status': 'stopped', 'id_session': 1}, 200
            return gettext('No answer from service.'), 500



