from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraService import TeraService
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
                    'type': 'integer'
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
                'parameters': {
                    'type': 'object'
                }
            },
            'required': ['action', 'id_service']
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

        if 'id_session' not in json_session_manager:
            json_session_manager['id_session'] = 0

        # Validate user rights if user can access that service
        if json_session_manager['id_service'] not in user_access.get_accessible_services_ids():
            return gettext('User doesn\'t have access to that service.'), 403

        # Get Redis key for service
        answer = None

        if 'id_service' in json_session_manager:
            service = TeraService.get_service_by_id(json_session_manager['id_service'])
            if not service:
                return gettext('Service not found'), 500
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
            # TODO: Move to services!!!
            if 'session' in answer:
                if 'session_uuid' in answer['session']:
                    session_uuid = answer['session']['session_uuid']

                    dest_topic_name = create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME)
                    tera_message = self.module.create_tera_message(dest=dest_topic_name)
                    if json_session_manager['action'] == 'start' or json_session_manager['action'] == 'invite':
                        join_session_msg = messages.JoinSessionEvent()
                        join_session_msg.session_uuid = session_uuid
                        join_session_msg.session_users.extend(answer['session']['session_users'])
                        join_session_msg.session_participants.extend(answer['session']['session_participants'])
                        join_session_msg.session_devices.extend(answer['session']['session_devices'])
                        any_message = messages.Any()
                        any_message.Pack(join_session_msg)
                        tera_message.data.extend([any_message])
                        self.module.publish(dest_topic_name, tera_message.SerializeToString())

                    if json_session_manager['action'] == 'stop':
                        stop_session_msg = messages.StopSessionEvent()
                        stop_session_msg.session_uuid = session_uuid
                        any_message = messages.Any()
                        any_message.Pack(stop_session_msg)
                        tera_message.data.extend([any_message])
                        self.module.publish(dest_topic_name, tera_message.SerializeToString())

                    if json_session_manager['action'] == 'remove':
                        leave_session_msg = messages.LeaveSessionEvent()
                        leave_session_msg.session_uuid = session_uuid
                        if 'session_users' in json_session_manager:
                            leave_session_msg.leaving_users.extend(json_session_manager['session_users'])
                        if 'session_participants' in json_session_manager:
                            leave_session_msg.leaving_participants.extend(json_session_manager['session_participants'])
                        if 'session_devices' in json_session_manager:
                            leave_session_msg.leaving_devices.extend(json_session_manager['session_devices'])
                        any_message = messages.Any()
                        any_message.Pack(leave_session_msg)
                        tera_message.data.extend([any_message])
                        self.module.publish(dest_topic_name, tera_message.SerializeToString())

            return answer, 200
        else:
            # Test and debug for now
            # if json_session_manager['action'] == 'start':
            #     return {'status': 'started', 'id_session': 1}, 200
            # if json_session_manager['action'] == 'stop':
            #     return {'status': 'stopped', 'id_session': 1}, 200
            return gettext('No answer from service.'), 500



