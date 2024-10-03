from flask import request
from flask_restx import Resource
from modules.LoginModule.LoginModule import participant_token_auth, current_participant
from modules.FlaskModule.FlaskModule import participant_api_ns as api
from modules.LoginModule.LoginModule import LoginModule
from opentera.redis.RedisVars import RedisVars

# Parser definition(s)
get_parser = api.parser()


class ParticipantRefreshToken(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Refresh token, old token needs to be passed in request headers.',
             responses={200: 'Success',
                        500: 'Server error'})
    @api.expect(get_parser)
    @participant_token_auth.login_required(role='full')
    def get(self):
        """
        Refresh participant dynamic token
        """
        # If we have made it this far, token passed in headers was valid.
        # Get user token key from redis

        token_key = self.module.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)

        # Get token for user
        # Put old token in disabled tokens
        scheme, old_token = request.headers['Authorization'].split(None, 1)
        if len(old_token) > 0:
            LoginModule.participant_add_disabled_token(old_token)

        # Regenerate token, 30 minutes expiration
        participant_token = current_participant.dynamic_token(token_key, expiration=60 * 30)

        # Return reply as json object
        reply = {"refresh_token": participant_token}

        return reply
