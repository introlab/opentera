from flask import session
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraDevice import TeraDevice
from libtera.redis.RedisRPCClient import RedisRPCClient
from modules.BaseModule import ModuleNames
from modules.DatabaseModule.DBManager import DBManager

get_parser = api.parser()
get_parser.add_argument('with_busy', type=inputs.boolean, help='Also return devices that are busy.')


class UserQueryOnlineDevices(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get online devices uuids.',
             responses={200: 'Success'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        parser = get_parser
        args = parser.parse_args()
        user_access = DBManager.userAccess(current_user)

        try:
            # rpc = RedisRPCClient(self.flaskModule.config.redis_config)
            # online_devices = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_devices')
            #
            # # Filter devices that are available to the query
            # devices_uuids = list(set(online_devices).intersection(user_access.get_accessible_devices_uuids()))
            #
            # return devices_uuids
            accessible_devices = user_access.get_accessible_devices_uuids()
            rpc = RedisRPCClient(self.flaskModule.config.redis_config)
            online_devices = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_devices')

            # Filter devices that are available to the query
            online_device_uuids = list(set(online_devices).intersection(accessible_devices))

            # Query device information
            devices = TeraDevice.query.filter(TeraDevice.device_uuid.in_(online_device_uuids)).all()
            devices_json = [device.to_json(minimal=True) for device in devices]
            for device in devices_json:
                device['device_online'] = True

            # Also query busy devices?
            if args['with_busy']:
                busy_devices = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'busy_devices')

                # Filter devices that are available to the query
                busy_device_uuids = list(set(busy_devices).intersection(accessible_devices))

                # Query device information
                busy_devices = TeraDevice.query.filter(TeraDevice.device_uuid.in_(busy_device_uuids)).all()
                busy_devices_json = [device.to_json(minimal=True) for device in busy_devices]
                for device in busy_devices_json:
                    device['device_busy'] = True
                devices_json.extend(busy_devices_json)

            return devices_json

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryOnlineDevices.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Internal server error when making RPC call.'), 500

    # def post(self):
    #     return '', 501
    #
    # def delete(self):
    #     return '', 501

