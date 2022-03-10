from flask import session, request
from flask_restx import Resource
from modules.LoginModule.LoginModule import LoginModule
from modules.DatabaseModule.DBManager import DBManager
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('token', type=str, help='Secret Token')
post_parser = api.parser()


class DeviceLogin(Resource):

    def __init__(self, _api, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)
        Resource.__init__(self, _api)

    @LoginModule.device_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Login device with Token.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def get(self):

        # Redis key is handled in LoginModule
        server_name = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']

        current_device = TeraDevice.get_device_by_uuid(session['_user_id'])
        current_device.update_last_online()
        args = get_parser.parse_args(strict=True)

        if 'X_EXTERNALSERVER' in request.headers:
            server_name = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        # Reply device information
        response = {'device_info': current_device.to_json(minimal=False)}

        device_access = DBManager.deviceAccess(current_device)

        # Reply participant information
        participants = device_access.get_accessible_participants()
        response['participants_info'] = list()

        for participant in participants:
            participant_info = {'participant_name': participant.participant_name,
                                'participant_uuid': participant.participant_uuid}
            response['participants_info'].append(participant_info)

        # Reply accessible sessions type ids
        session_types = device_access.get_accessible_session_types()
        response['session_types_info'] = list()

        for st in session_types:
            response['session_types_info'].append(st.to_json(minimal=True))

        # TODO Handle sessions
        if current_device.device_onlineable:
            if not self.test:
                # Verify if device already logged in
                rpc = RedisRPCClient(self.flaskModule.config.redis_config)
                online_devices = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_devices')

                if online_devices is None:
                    return gettext('Unable to get online devices.'), 403

                if current_device.device_uuid in online_devices:
                    self.flaskModule.logger.log_warning(self.flaskModule.module_name,
                                                        DeviceLogin.__name__,
                                                        'get', 403,
                                                        'Device already logged in', current_device.to_json(minimal=True))

                    return gettext('Device already logged in.'), 403

            # Permanent ?
            session.permanent = True

            print('DeviceLogin - setting key with expiration in 60s', session['_id'], session['_user_id'])
            self.flaskModule.redisSet(session['_id'], session['_user_id'], ex=60)

            # Add websocket URL
            response['websocket_url'] = "wss://" + server_name + ":" + str(port) + "/wss/device?id=" + session['_id']

        # Return reply as json object
        return response
