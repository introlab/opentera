from flask import jsonify, session, request
from flask_restx import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule
from flask_babel import gettext
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
import json

# Parser definition(s)
# get_parser = api.parser()
post_parser = api.parser()
post_parser.add_argument('token', type=str, help='Secret Token')

status_schema = api.schema_model('device_status', {
    'type': 'object',
    'properties': {
        'status': {
            'type': 'object'
            },
        'timestamp': {
            'type': 'number'
            },
        },
    'required': ['status', 'timestamp']
})


class DeviceQueryStatus(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)
        self.user_manager_module = kwargs.get('user_manager_module', None)

    @LoginModule.device_token_or_certificate_required
    @api.expect(status_schema)
    @api.expect(post_parser)
    @api.doc(description='Set the device status (will update UserManagerModule).',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def post(self):
        current_device = TeraDevice.get_device_by_uuid(session['_user_id'])

        # status_schema.validate(request.json)
        # This should not be required since schema should be validated first.
        if 'status' not in request.json or 'timestamp' not in request.json:
            return gettext('Missing arguments'), 400

        # Call UserManagerModule RPC interface to update status
        # This will generate a DeviceEvent of type DEVICE_STATUS_CHANGED for everybody
        # subscribed to UserManagerModule events.
        if not self.test:
            rpc = RedisRPCClient(self.module.config.redis_config)

            ret = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'update_device_status',
                           current_device.device_uuid, json.dumps(request.json['status']), request.json['timestamp'])
        else:
            # TESTING ONLY
            ret = None
            if self.user_manager_module:
                ret = self.user_manager_module.update_device_status_rpc_callback(str(current_device.device_uuid),
                                                                                 json.dumps(request.json['status']),
                                                                                 str(request.json['timestamp']))
        # None will be returned by UserManagerModule if device is offline
        if ret is None:
            return gettext('Status update forbidden on offline device.'), 403

        # Will return the status set in the UserManagerModule
        return ret

