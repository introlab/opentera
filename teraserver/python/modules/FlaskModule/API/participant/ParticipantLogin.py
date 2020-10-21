from flask import jsonify, session, request
from flask_restx import Resource, reqparse, fields
from flask_babel import gettext
from modules.LoginModule.LoginModule import participant_multi_auth, current_participant
from modules.FlaskModule.FlaskModule import participant_api_ns as api
from modules.RedisVars import RedisVars
from libtera.redis.RedisRPCClient import RedisRPCClient
from modules.BaseModule import ModuleNames


# Parser definition(s)
get_parser = api.parser()
post_parser = api.parser()

model = api.model('ParticipantLogin', {
    'websocket_url': fields.String,
    'participant_uuid': fields.String,
    'participant_token': fields.String,
    'base_token': fields.String
})


class ParticipantLogin(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    # @participant_http_auth.login_required
    @participant_multi_auth.login_required(role='limited')
    @api.expect(get_parser)
    @api.doc(description='Participant login with HTTPAuth',
             responses={200: 'Success - Login succeeded',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @api.marshal_with(model, mask=None)
    def get(self):
        if current_participant:

            # Verify if participant already logged in
            rpc = RedisRPCClient(self.module.config.redis_config)
            online_participants = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_participants')
            if current_participant.participant_uuid in online_participants:
                self.module.logger.log_warning(self.module.module_name,
                                               ParticipantLogin.__name__,
                                               'get', 403,
                                               'Participant already logged in',
                                               current_participant.to_json(minimal=True))
                return gettext('Participant already logged in.'), 403

            current_participant.update_last_online()
            session.permanent = True

            # Redis key is handled in LoginModule
            servername = self.module.config.server_config['hostname']
            port = self.module.config.server_config['port']

            if 'X_EXTERNALHOST' in request.headers:
                if ':' in request.headers['X_EXTERNALHOST']:
                    servername, port = request.headers['X_EXTERNALHOST'].split(':', 1)
                else:
                    servername = request.headers['X_EXTERNALHOST']

            if 'X_EXTERNALPORT' in request.headers:
                port = request.headers['X_EXTERNALPORT']

            print('ParticipantLogin - setting key with expiration in 60s', session['_id'], session['_user_id'])
            self.module.redisSet(session['_id'], session['_user_id'], ex=60)

            # Return reply as json object
            reply = {"websocket_url": "wss://" + servername + ":"
                                      + str(port) + "/wss/participant?id=" + session['_id'],
                     "participant_name": current_participant.participant_name,
                     "participant_uuid": session['_user_id']}

            # Set token according to API access (http auth is full access, token is not)
            if current_participant.fullAccess:
                token_key = self.module.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)
                reply['participant_token'] = current_participant.dynamic_token(token_key)
                reply['base_token'] = current_participant.participant_token
            else:
                reply['base_token'] = current_participant.participant_token

            return reply
        else:
            self.module.logger.log_error(self.module.module_name,
                                         ParticipantLogin.__name__,
                                         'get', 501, 'Missing current_participant')
            return gettext('Missing current_participant'), 501


