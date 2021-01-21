from flask import session, request
from flask_restx import Resource, reqparse
from modules.LoginModule.LoginModule import user_token_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.LoginModule.LoginModule import LoginModule

# Parser definition(s)
get_parser = api.parser()


class UserRefreshToken(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.parser = reqparse.RequestParser()

    @user_token_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Refresh token, old token needs to be passed in request headers.',
             responses={200: 'Success',
                        500: 'Server error'})
    def get(self):
        # If we have made it this far, token passed in headers was valid.
        # Get user token key from redis
        from opentera.redis.RedisVars import RedisVars
        token_key = self.module.redisGet(RedisVars.RedisVar_UserTokenAPIKey)

        # Get token for user
        from opentera.db.models.TeraUser import TeraUser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])

        # Put old token in disabled tokens
        scheme, old_token = request.headers['Authorization'].split(None, 1)
        if len(old_token) > 0:
            LoginModule.user_push_disabled_token(old_token)

        # Regenerate token, 30 minutes expiration
        user_token = current_user.get_token(token_key, expiration=60 * 30)

        # Return reply as json object
        reply = {"refresh_token": user_token}

        return reply
