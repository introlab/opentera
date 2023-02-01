from flask import session, request
from flask_restx import Resource, fields, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import participant_multi_auth, current_participant
from modules.FlaskModule.FlaskModule import participant_api_ns as api
from opentera.redis.RedisVars import RedisVars
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from opentera.utils.UserAgentParser import UserAgentParser
import opentera.messages.python as messages

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('with_websocket', type=inputs.boolean, help='If set, requires that a websocket url is returned.'
                                                                    'If not possible to do so, return a 403 error.')

model = api.model('ParticipantLogin', {
    'websocket_url': fields.String,
    'participant_uuid': fields.String,
    'participant_token': fields.String,
    'participant_name': fields.String,
    'base_token': fields.String
})


class ParticipantLogin(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Participant login with HTTPAuth',
             responses={200: 'Success - Login succeeded',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @api.expect(get_parser)
    @participant_multi_auth.login_required(role='limited')
    def get(self):
        if current_participant:
            args = get_parser.parse_args()

            servername = self.module.config.server_config['hostname']
            port = self.module.config.server_config['port']

            if 'X_EXTERNALSERVER' in request.headers:
                servername = request.headers['X_EXTERNALSERVER']

            if 'X_EXTERNALPORT' in request.headers:
                port = request.headers['X_EXTERNALPORT']

            # Get login informations for log
            login_infos = UserAgentParser.parse_request_for_login_infos(request)
            if current_participant.fullAccess:
                login_type = messages.LoginEvent.LOGIN_TYPE_TOKEN
            else:
                login_type = messages.LoginEvent.LOGIN_TYPE_PASSWORD

            # Verify if participant already logged in
            rpc = RedisRPCClient(self.module.config.redis_config)
            if not self.test:
                online_participants = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_participants')
            else:
                online_participants = []
            websocket_url = None
            if current_participant.participant_uuid not in online_participants:
                websocket_url = "wss://" + servername + ":" + str(port) + "/wss/participant?id=" + session['_id']
                print('ParticipantLogin - setting key with expiration in 60s', session['_id'], session['_user_id'])
                self.module.redisSet(session['_id'], session['_user_id'], ex=60)
            elif args['with_websocket']:
                # Online and websocket required
                # self.module.logger.log_warning(self.module.module_name,
                #                                ParticipantLogin.__name__,
                #                                'get', 403,
                #                                'Participant already logged in',
                #                                current_participant.to_json(minimal=True))
                self.module.logger.send_login_event(sender=self.module.module_name,
                                                    level=messages.LogEvent.LOGLEVEL_ERROR,
                                                    login_type=login_type,
                                                    login_status=
                                                    messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_ALREADY_LOGGED_IN,
                                                    client_name=login_infos['client_name'],
                                                    client_version=login_infos['client_version'],
                                                    client_ip=login_infos['client_ip'],
                                                    os_name=login_infos['os_name'],
                                                    os_version=login_infos['os_version'],
                                                    participant_uuid=current_participant.participant_uuid,
                                                    server_endpoint=login_infos['server_endpoint'])
                return gettext('Participant already logged in.'), 403

            current_participant.update_last_online()

            # Return reply as json object
            reply = {"participant_name": current_participant.participant_name,
                     "participant_uuid": session['_user_id']}
            if websocket_url:
                reply["websocket_url"] = websocket_url

            # Set token according to API access (http auth is full access, token is not)
            if current_participant.fullAccess:
                token_key = self.module.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)
                reply['participant_token'] = current_participant.dynamic_token(token_key)
                reply['base_token'] = current_participant.participant_token
            else:
                reply['base_token'] = current_participant.participant_token

            self.module.logger.send_login_event(sender=self.module.module_name,
                                                level=messages.LogEvent.LOGLEVEL_INFO,
                                                login_type=login_type,
                                                login_status=messages.LoginEvent.LOGIN_STATUS_SUCCESS,
                                                client_name=login_infos['client_name'],
                                                client_version=login_infos['client_version'],
                                                client_ip=login_infos['client_ip'],
                                                os_name=login_infos['os_name'],
                                                os_version=login_infos['os_version'],
                                                participant_uuid=current_participant.participant_uuid,
                                                server_endpoint=login_infos['server_endpoint'])
            return reply
        else:
            self.module.logger.log_error(self.module.module_name,
                                         ParticipantLogin.__name__,
                                         'get', 501, 'Missing current_participant')
            return gettext('Missing current_participant'), 501
