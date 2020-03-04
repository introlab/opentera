from flask import jsonify, session
from flask_restplus import Resource, reqparse, fields
from modules.LoginModule.LoginModule import participant_http_auth, current_participant
from modules.FlaskModule.FlaskModule import participant_api_ns as api


# Parser definition(s)
get_parser = api.parser()
post_parser = api.parser()

model = api.model('ParticipantLogin', {
    'websocket_url': fields.String,
    'participant_uuid': fields.String,
    'participant_token': fields.String
})


class ParticipantLogin(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @participant_http_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Participant login with HTTPAuth',
             responses={200: 'Success - Login succeeded',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @api.marshal_with(model, mask=None)
    def get(self):
        if current_participant:
            session.permanent = True

            # Redis key is handled in LoginModule
            servername = self.module.config.server_config['hostname']
            port = self.module.config.server_config['port']

            # Return reply as json object
            reply = {"websocket_url": "wss://" + servername + ":"
                                      + str(port) + "/wss/participant?id=" + session['_id'],
                     "participant_uuid": session['_user_id'],
                     "participant_token": current_participant.participant_token}

            return reply
        else:
            return 'Missing current_participant', 501

