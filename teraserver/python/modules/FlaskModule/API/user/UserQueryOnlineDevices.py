from flask import session
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraDevice import TeraDevice
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from modules.DatabaseModule.DBManager import DBManager

get_parser = api.parser()


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
            accessible_devices = user_access.get_accessible_devices_uuids()
            rpc = RedisRPCClient(self.flaskModule.config.redis_config)
            status_devices = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'status_devices')

            devices_uuids = [device_uuid for device_uuid in status_devices]
            # Filter devices that are available to the query
            filtered_devices_uuids = list(set(devices_uuids).intersection(accessible_devices))

            # Query device information
            devices = TeraDevice.query.filter(TeraDevice.device_uuid.in_(filtered_devices_uuids)).all()
            devices_json = [device.to_json(minimal=True) for device in devices]
            for device in devices_json:
                device['device_online'] = status_devices[device['device_uuid']]['online']
                device['device_busy'] = status_devices[device['device_uuid']]['busy']

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

