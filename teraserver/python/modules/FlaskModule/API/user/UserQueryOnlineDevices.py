from flask import jsonify, session
from flask_restx import Resource, reqparse
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.redis.RedisRPCClient import RedisRPCClient
from modules.BaseModule import ModuleNames
from modules.DatabaseModule.DBManager import DBManager
from messages.python.RPCMessage_pb2 import RPCMessage, Value
from twisted.internet import defer
import datetime


class UserQueryOnlineDevices(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        self.parser = reqparse.RequestParser()

    @user_multi_auth.login_required
    @api.doc(description='Get online devices uuids.',
             responses={200: 'Success'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        args = self.parser.parse_args()
        user_access = DBManager.userAccess(current_user)

        try:
            rpc = RedisRPCClient(self.flaskModule.config.redis_config)
            online_devices = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_devices')

            # Filter devices that are available to the querier
            devices_uuids = list(set(online_devices).intersection(user_access.get_accessible_devices_uuids()))

            return devices_uuids

        except InvalidRequestError:
            return gettext('Internal server error when making RPC call.'), 500

    # def post(self):
    #     return '', 501
    #
    # def delete(self):
    #     return '', 501

