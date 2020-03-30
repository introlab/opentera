from flask import jsonify, session
from flask_restplus import Resource, reqparse
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.redis.RedisRPCClient import RedisRPCClient
from modules.BaseModule import ModuleNames
from messages.python.RPCMessage_pb2 import RPCMessage, Value
from twisted.internet import defer
import datetime


class QueryOnlineUsers(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        self.parser = reqparse.RequestParser()

    @user_multi_auth.login_required
    @api.doc(description='Get online users. CURRENTLY UNIMPLEMENTED.',
             responses={200: 'Success'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        args = self.parser.parse_args()

        my_args = {}

        try:
            rpc = RedisRPCClient(self.flaskModule.config.redis_config)
            val = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_users')
            return jsonify(val)
        except InvalidRequestError:
            return '', 500

    # def post(self):
    #     return '', 501
    #
    # def delete(self):
    #     return '', 501

