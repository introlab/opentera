from flask import jsonify, session, request
from flask_restx import Resource, reqparse, fields
from modules.LoginModule.LoginModule import user_http_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api


model = api.model('Login', {
    'websocket_url': fields.String,
    'user_uuid': fields.String,
    'user_token': fields.String
})


class Login(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.parser = reqparse.RequestParser()

    @user_http_auth.login_required
    @api.doc(description='Login to the server using HTTP Basic Authentification (HTTPAuth)')
    @api.marshal_with(model, mask=None)
    def get(self):

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

        # Get user token key from redis
        from modules.RedisVars import RedisVars
        token_key = self.module.redisGet(RedisVars.RedisVar_UserTokenAPIKey)

        # Get token for user
        from libtera.db.models.TeraUser import TeraUser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_token = current_user.get_token(token_key)

        print('Login - setting key with expiration in 60s', session['_id'], session['_user_id'])
        self.module.redisSet(session['_id'], session['_user_id'], ex=60)

        # Return reply as json object
        reply = {"websocket_url": "wss://" + servername + ":" + str(port) + "/wss/user?id=" + session['_id'],
                 "user_uuid": session['_user_id'],
                 "user_token": user_token}

        return reply
