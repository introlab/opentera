from flask import session, request
from flask_restx import Resource
from modules.LoginModule.LoginModule import LoginModule, current_device
from modules.DatabaseModule.DBManager import DBManager
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from opentera.utils.UserAgentParser import UserAgentParser
from flask_babel import gettext
import opentera.messages.python as messages

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('token', type=str, help='Secret Token')


class DeviceLogin(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Login device with Token.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    @api.expect(get_parser)
    @LoginModule.device_token_or_certificate_required
    def get(self):
        # Redis key is handled in LoginModule
        server_name = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']

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

        # Get login informations for log
        login_infos = UserAgentParser.parse_request_for_login_infos(request)
        if request.headers.__contains__('X-Device-Uuid'):
            login_type = messages.LoginEvent.LOGIN_TYPE_CERTIFICATE
        else:
            login_type = messages.LoginEvent.LOGIN_TYPE_TOKEN

        # TODO Handle sessions
        if current_device.device_onlineable:
            if not self.test:
                # Verify if device already logged in
                rpc = RedisRPCClient(self.module.config.redis_config)
                online_devices = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_devices')

                if online_devices is None:
                    return gettext('Unable to get online devices.'), 403

                if current_device.device_uuid in online_devices:
                    self.module.logger.send_login_event(sender=self.module.module_name,
                                                        level=messages.LogEvent.LOGLEVEL_ERROR,
                                                        login_type=login_type,
                                                        login_status=
                                                        messages.LoginEvent.LOGIN_STATUS_FAILED_WITH_ALREADY_LOGGED_IN,
                                                        client_name=login_infos['client_name'],
                                                        client_version=login_infos['client_version'],
                                                        client_ip=login_infos['client_ip'],
                                                        os_name=login_infos['os_name'],
                                                        os_version=login_infos['os_version'],
                                                        device_uuid=current_device.device_uuid,
                                                        server_endpoint=login_infos['server_endpoint'])

                    return gettext('Device already logged in.'), 403

            print('DeviceLogin - setting key with expiration in 60s', session['_id'], session['_user_id'])
            self.module.redisSet(session['_id'], session['_user_id'], ex=60)

            # Add websocket URL
            response['websocket_url'] = "wss://" + server_name + ":" + str(port) + "/wss/device?id=" + session['_id']

        self.module.logger.send_login_event(sender=self.module.module_name,
                                            level=messages.LogEvent.LOGLEVEL_INFO,
                                            login_type=login_type,
                                            login_status=messages.LoginEvent.LOGIN_STATUS_SUCCESS,
                                            client_name=login_infos['client_name'],
                                            client_version=login_infos['client_version'],
                                            client_ip=login_infos['client_ip'],
                                            os_name=login_infos['os_name'],
                                            os_version=login_infos['os_version'],
                                            device_uuid=current_device.device_uuid,
                                            server_endpoint=login_infos['server_endpoint'])
        # Return reply as json object
        return response
