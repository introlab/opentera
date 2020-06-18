import services.VideoRehabService.Globals as Globals
from services.shared.modules.WebRTCModule import WebRTCModule
from libtera.redis.RedisClient import RedisClient
from services.VideoRehabService.ConfigManager import ConfigManager
from modules.RedisVars import RedisVars

# Twisted
from twisted.application import internet, service
from twisted.internet import reactor, ssl, defer
from twisted.python.threadpool import ThreadPool
from twisted.web.http import HTTPChannel
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.python import log
import messages.python as messages
import sys
import os
import uuid

# Flask Module
from services.VideoRehabService.FlaskModule import FlaskModule
from services.shared.ServiceOpenTera import ServiceOpenTera


class VideoRehabService(ServiceOpenTera):
    def __init__(self, config_man: ConfigManager, service_info):
        ServiceOpenTera.__init__(self, config_man, service_info)

        self.application = service.Application(self.config['name'])

        # Create REST backend
        self.flaskModule = FlaskModule(Globals.config_man)

        # Create twisted service
        self.flaskModuleService = self.flaskModule.create_service()

        # Connect our services to the application, just like a normal service.
        self.flaskModuleService.setServiceParent(self.application)

        # Create WebRTCModule
        self.webRTCModule = WebRTCModule(config_man)

    def notify_service_messages(self, pattern, channel, message):
        pass

    def setup_rpc_interface(self):
        # TODO Update rpc interface
        self.rpc_api['session_manage'] = {'args': ['str:json_info'],
                                          'returns': 'dict',
                                          'callback': self.session_manage}

    def session_manage(self, json_str):

        # - Service will create session if needed or reuse existing one
        # - Service will send invitations / updates to participants / users
        # - Service will return id_session and status code as a result to the RPC call and this will be the reply of
        #   this query
        import json
        try:

            session_manage = json.loads(json_str)

            if 'session_manage' in session_manage:
                session_manage_args = session_manage['session_manage']
                # Get all arguments
                # TODO VALIDATE ARGUMENTS

                # Get "common" arguments
                action = session_manage_args['action']
                id_service = session_manage_args['id_service']
                id_creator_user = session_manage_args['id_creator_user']
                id_session_type = session_manage_args['id_session_type']

                if action == 'start':
                    # Get additional "start" arguments
                    parameters = session_manage_args['parameters']
                    participants = session_manage_args['session_participants']
                    users = session_manage_args['session_users']
                    # TODO handle devices
                    devices = []

                    # Call service API to create session
                    api_req = {'create_session': {'id_service': id_service,
                                                  'id_creator_user': id_creator_user,
                                                  'id_session_type': id_session_type,
                                                  'participants': participants,
                                                  'users': users,
                                                  'devices': devices}
                               }

                    api_response = self.post_to_opentera('/api/service/sessions', api_req)

                    if api_response.status_code == 200:

                        session_info = api_response.json()

                        # Replace fields with uuids
                        session_info['session_participants'] = participants
                        session_info['session_users'] = users
                        session_info['session_devices'] = devices

                        # Add session key
                        session_info['session_key'] = str(uuid.uuid4())

                        # Start webrtc process
                        retval, process_info = self.webRTCModule.create_webrtc_session(
                            session_info['session_key'], id_creator_user, users, participants, devices)

                        if not retval or not process_info:
                            return {'Error': 'Cannot create process'}

                        session_info['session_url'] = process_info['url']

                        # message
                        # JoinSessionEvent
                        # {
                        #     string
                        # session_url = 1;
                        # string
                        # session_creator_name = 2;
                        # string
                        # session_uuid = 3;
                        # repeated
                        # string
                        # session_participants = 4;
                        # repeated
                        # string
                        # session_users = 5;
                        # repeated
                        # string
                        # session_devices = 6;
                        # string
                        # join_msg = 7;
                        # string
                        # session_parameters = 8;
                        # string
                        # service_uuid = 9;
                        # }


                        # Fill event information
                        joinMessage = messages.JoinSessionEvent()
                        joinMessage.session_url = session_info['session_url']
                        joinMessage.session_creator_name = session_info['session_creator_user']
                        joinMessage.session_uuid = session_info['session_uuid']
                        for user_uuid in users:
                            joinMessage.session_users.extend([user_uuid])
                        for participant_uuid in participants:
                            joinMessage.session_participants.extend([participant_uuid])
                        for device_uuid in devices:
                            joinMessage.session_devices.extend([device_uuid])
                        joinMessage.join_msg = 'Hello World'
                        joinMessage.session_parameters = ''
                        joinMessage.service_uuid = self.service_uuid

                        # Send invitations (as events)
                        for user_uuid in users:
                            self.send_event_message(joinMessage, 'websocket.user.'
                                                    + user_uuid + '.events')

                        for participant_uuid in participants:
                            self.send_event_message(joinMessage, 'websocket.participant.'
                                                    + participant_uuid + '.events')

                        for device_uuid in devices:
                            self.send_event_message(joinMessage, 'websocket.device.'
                                                    + device_uuid + '.events')

                        # Return session information
                        return session_info

                    else:
                        return {'Error': 'Cannot create session'}

                elif action == 'stop':
                    id_session = session_manage_args['id_session']
                    pass

                return None
        except json.JSONDecodeError as e:
            print('Error', e)
            return None

        return None


if __name__ == '__main__':

    # Very first thing, log to stdout
    log.startLogging(sys.stdout)

    # Load configuration
    if not Globals.config_man.load_config('VideoRehabService.json'):
        print('Invalid config')

    # Global redis client
    Globals.redis_client = RedisClient(Globals.config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)

    # Get service UUID
    service_info = Globals.redis_client.redisGet(RedisVars.RedisVar_ServicePrefixKey +
                                                 Globals.config_man.service_config['name'])
    import sys
    if service_info is None:
        sys.stderr.write('Error: Unable to get service info from OpenTera Server - is the server running and config '
                         'correctly set in this service?')
        exit(1)
    import json
    service_info = json.loads(service_info)
    if 'service_uuid' not in service_info:
        sys.stderr.write('OpenTera Server didn\'t return a valid service UUID - aborting.')
        exit(1)

    # Update service uuid
    Globals.config_man.service_config['ServiceUUID'] = service_info['service_uuid']

    # Update port, hostname, endpoint
    Globals.config_man.service_config['port'] = service_info['service_port']
    Globals.config_man.service_config['hostname'] = service_info['service_hostname']

    # Create the Service
    service = VideoRehabService(Globals.config_man, service_info)

    # Start App / reactor events
    reactor.run()
