from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraService import TeraService
from modules.RedisVars import RedisVars
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
                'id_session': {
                    'type': 'integer'
                },
                'id_service': {
                    'type': 'integer'
                },
                'id_creator_user': {
                    'type': 'integer'
                },
                'session_participants': {
                    'type': 'array',
                    'uniqueItems': True,
                    'contains': {
                        'type': 'string',
                        'format': 'uuid'
                    }
                },
                'session_users': {
                    'type': 'array',
                    'uniqueItems': True,
                    'contains': {
                        'type': 'string',
                        'format': 'uuid'
                    }
                },
                'session_devices': {
                    'type': 'array',
                    'uniqueItems': True,
                    'contains': {
                        'type': 'string',
                        'format': 'uuid'
                    }
                },
                'action': {
                    'type': 'string'  # 'start', 'stop', 'status', 'resume'
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
    # @api.expect(session_manager_schema, validate=True)
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

        if 'id_service' not in json_session_manager:
            return gettext('Missing session id'), 400

        if 'id_creator_user' not in json_session_manager:
            json_session_manager['id_creator_user'] = current_user.id_user

        # Validate user rights if user can access that service
        if json_session_manager['id_service'] not in user_access.get_accessible_services_ids():
            return gettext('User doesn\'t have access to that service.'), 403

        # Get Redis key for service
        service = TeraService.get_service_by_id(json_session_manager['id_service'])
        if not service:
            return gettext('Service not found'), 500

        rpc = RedisRPCClient(self.module.config.redis_config)
        answer = rpc.call_service(service.service_key, 'session_manage', json.dumps(request.json))

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
            return answer, 200
        else:
            return None, 500


