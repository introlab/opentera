import services.VideoRehabService.Globals as Globals
from services.shared.modules.WebRTCModule import WebRTCModule
from libtera.redis.RedisClient import RedisClient
from libtera.db.models.TeraSession import TeraSessionStatus
from services.VideoRehabService.ConfigManager import ConfigManager
from services.shared.ServiceAccessManager import ServiceAccessManager
from modules.RedisVars import RedisVars
from modules.BaseModule import ModuleNames, create_module_message_topic_from_name, create_module_event_topic_from_name
from google.protobuf.json_format import Parse, ParseError
from google.protobuf.message import DecodeError

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
from flask_babel import gettext


class VideoRehabService(ServiceOpenTera):
    def __init__(self, config_man: ConfigManager, this_service_info):
        ServiceOpenTera.__init__(self, config_man, this_service_info)

        # self.application = service.Application(self.config['name'])

        # Create REST backend
        self.flaskModule = FlaskModule(Globals.config_man)

        # Create twisted service
        self.flaskModuleService = self.flaskModule.create_service()

        # Connect our services to the application, just like a normal service.
        # self.flaskModuleService.setServiceParent(self.application)

        # Create WebRTCModule
        self.webRTCModule = WebRTCModule(config_man)

        # Active sessions
        self.sessions = dict()

    def notify_service_messages(self, pattern, channel, message):
        pass

    @defer.inlineCallbacks
    def register_to_events(self):
        # Need to register to events produced by UserManagerModule
        ret1 = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
            ModuleNames.USER_MANAGER_MODULE_NAME), self.user_manager_event_received)

        print(ret1)

    def user_manager_event_received(self, pattern, channel, message):
        print('VideoRehabService - user_manager_event_received', pattern, channel, message)
        try:
            tera_event = messages.TeraEvent()
            if isinstance(message, str):
                ret = tera_event.ParseFromString(message.encode('utf-8'))
            elif isinstance(message, bytes):
                ret = tera_event.ParseFromString(message)

            user_event = messages.UserEvent()
            participant_event = messages.ParticipantEvent()
            device_event = messages.DeviceEvent()

            # Look for UserEvent, ParticipantEvent, DeviceEvent
            for any_msg in tera_event.events:
                if any_msg.Unpack(user_event):
                    self.handle_user_event(user_event)
                if any_msg.Unpack(participant_event):
                    self.handle_participant_event(participant_event)
                if any_msg.Unpack(device_event):
                    self.handle_device_event(device_event)

        except DecodeError as d:
            print('VideoRehabService - DecodeError ', pattern, channel, message, d)
        except ParseError as e:
            print('VideoRehabService - Failure in redisMessageReceived', e)

    def handle_user_event(self, event: messages.UserEvent):
        print('VideoRehabService.handle_user_event', event)
        # Verify each session
        for id_session in self.sessions:
            session_info = self.sessions[id_session]

            # Verify if it contains the user_uuid
            if event.user_uuid in session_info['session_users']:
                # Verify the event type
                if event.type == messages.UserEvent.USER_CONNECTED:
                    # Resend invitation to newly connected user
                    print('Resending invitation to ', event, session_info)

                    join_message = messages.JoinSessionEvent()

                    # Fill information for join_message
                    join_message.session_url = session_info['session_url']
                    join_message.session_creator_name = session_info['session_creator_user']
                    join_message.session_uuid = session_info['session_uuid']
                    for user_uuid in session_info['session_users']:
                        join_message.session_users.extend([user_uuid])
                    for participant_uuid in session_info['session_participants']:
                        join_message.session_participants.extend([participant_uuid])
                    for device_uuid in session_info['session_devices']:
                        join_message.session_devices.extend([device_uuid])

                    # Send message
                    self.send_event_message(join_message, 'websocket.user.' + event.user_uuid + '.events')

                elif event.type == messages.UserEvent.USER_DISCONNECTED:
                    # Terminate session if last user ?
                    if 'session_creator_user_uuid' in session_info:
                        if session_info['session_creator_user_uuid'] == event.user_uuid:
                            manage_session_args = {'id_session': id_session}
                            self.manage_stop_session(manage_session_args)
                            # End loop, sessions dict will be changed in manage_stop_session
                            break

    def handle_participant_event(self, event: messages.ParticipantEvent):
        print('VideoRehabService.handle_participant_event', event)
        # Verify each session
        for id_session in self.sessions:
            session_info = self.sessions[id_session]

            # Verify if it contains the user_uuid
            if event.participant_uuid in session_info['session_participants']:
                # Verify the event type
                if event.type == messages.ParticipantEvent.PARTICIPANT_CONNECTED:
                    # Resend invitation to newly connected user
                    print('Resending invitation to ', event, session_info)

                    join_message = messages.JoinSessionEvent()

                    # Fill information for join_message
                    join_message.session_url = session_info['session_url']
                    join_message.session_creator_name = session_info['session_creator_user']
                    join_message.session_uuid = session_info['session_uuid']
                    for user_uuid in session_info['session_users']:
                        join_message.session_users.extend([user_uuid])
                    for participant_uuid in session_info['session_participants']:
                        join_message.session_participants.extend([participant_uuid])
                    for device_uuid in session_info['session_devices']:
                        join_message.session_devices.extend([device_uuid])

                    # Send message
                    self.send_event_message(join_message, 'websocket.participant.' + event.participant_uuid + '.events')

                elif event.type == messages.ParticipantEvent.PARTICIPANT_DISCONNECTED:
                    # Nothing to do?
                    pass

    def handle_device_event(self, event: messages.DeviceEvent):
        print('VideoRehabService.handle_device_event', event)
        # Verify each session
        for id_session in self.sessions:
            session_info = self.sessions[id_session]

            # Verify if it contains the user_uuid
            if event.device_uuid in session_info['session_devices']:
                # Verify the event type
                if event.type == messages.DeviceEvent.DEVICE_CONNECTED:
                    # Resend invitation to newly connected user
                    print('Resending invitation to ', event, session_info)

                    join_message = messages.JoinSessionEvent()

                    # Fill information for join_message
                    join_message.session_url = session_info['session_url']
                    join_message.session_creator_name = session_info['session_creator_user']
                    join_message.session_uuid = session_info['session_uuid']
                    for user_uuid in session_info['session_users']:
                        join_message.session_users.extend([user_uuid])
                    for participant_uuid in session_info['session_participants']:
                        join_message.session_participants.extend([participant_uuid])
                    for device_uuid in session_info['session_devices']:
                        join_message.session_devices.extend([device_uuid])

                    # Send message
                    self.send_event_message(join_message, 'websocket.device.' + event.device_uuid + '.events')

                elif event.type == messages.DeviceEvent.DEVICE_DISCONNECTED:
                    # Nothing to do?
                    pass

    def nodejs_webrtc_message_callback(self, pattern, channel, message):
        print('WebRTCModule - nodejs_webrtc_message_callback', pattern, channel, message)
        parts = channel.split(".")
        if len(parts) == 2:
            session_key = parts[1]
            print(session_key)
            if message == 'Ready!':
                print('Ready!')
                self.handle_nodejs_session_ready(session_key)

    def get_session_info_from_key(self, session_key):
        for session_id in self.sessions:
            if self.sessions[session_id]['session_key'] == session_key:
                return self.sessions[session_id]
        return None

    def handle_nodejs_session_ready(self, session_key):
        # Should send invitations
        session_info = self.get_session_info_from_key(session_key)

        if session_info:

            users = session_info['session_users']
            participants = session_info['session_participants']
            devices = session_info['session_devices']
            parameters = session_info['session_parameters']

            # Create event
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
            joinMessage.join_msg = gettext('Join Session')
            joinMessage.session_parameters = parameters
            joinMessage.service_uuid = self.service_uuid

            # Send invitations (as events) for users, participants and devices
            for user_uuid in users:
                self.send_event_message(joinMessage, 'websocket.user.'
                                        + user_uuid + '.events')
            for participant_uuid in participants:
                self.send_event_message(joinMessage, 'websocket.participant.'
                                        + participant_uuid + '.events')
            for device_uuid in devices:
                self.send_event_message(joinMessage, 'websocket.device.'
                                        + device_uuid + '.events')

    def setup_rpc_interface(self):
        # TODO Update rpc interface
        self.rpc_api['session_manage'] = {'args': ['str:json_info'],
                                          'returns': 'dict',
                                          'callback': self.session_manage}

        self.rpc_api['participant_info'] = {'args': ['str:participant_uuid'],
                                            'returns': 'dict',
                                            'callback': self.participant_info}

    def participant_info(self, participant_uuid):
        # Getting participant info from uuid
        params = {'participant_uuid': participant_uuid}
        response = self.get_from_opentera('/api/service/participants', params)
        if response.status_code == 200:
            return response.json()
        return {}

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

                if action == 'start':
                    return self.manage_start_session(session_manage_args)
                elif action == 'stop':
                    return self.manage_stop_session(session_manage_args)

        except json.JSONDecodeError as e:
            print('Error', e)
            return None

        return None

    def manage_stop_session(self, session_manage_args: dict):
        id_session = session_manage_args['id_session']
        # id_service = session_manage_args['id_service']
        # id_creator_user = session_manage_args['id_creator_user']

        if id_session in self.sessions:
            session_info = self.sessions[id_session]
            # Room name = key
            self.webRTCModule.stop_webrtc_session(session_info['session_key'])

            # Unsubscribe to messages from this process
            self.unsubscribe_pattern_with_callback('webrtc.' + session_info['session_key'],
                                                   self.nodejs_webrtc_message_callback)

            # Call service API for session changes...

            # Create session stop event
            from datetime import datetime
            api_req = {'session_event': {'id_session_event': 0,
                                         'id_session': id_session,
                                         'id_session_event_type': 4,  # STOP session event
                                         'session_event_datetime': str(datetime.now()),
                                         'session_event_context': self.service_info['service_key']
                                         }
                       }

            api_response = self.post_to_opentera('/api/service/sessions/events', api_req)

            if api_response.status_code != 200:
                return {'status': 'error', 'error_text': gettext('Cannot create STOP session event')}

            # Compute session duration from last start event
            duration = 0

            for session_event in session_info['session_events']:
                if session_event['id_session_event_type'] == 3:  # START event
                    time_diff = datetime.now() - datetime.strptime(session_event['session_event_datetime'],
                                                                   '%Y-%m-%dT%H:%M:%S.%f')
                    duration = int(time_diff.total_seconds())

            # Default duration
            if duration == 0:
                time_diff = datetime.now() - datetime.strptime(
                    session_info['session_start_datetime'], '%Y-%m-%dT%H:%M:%S.%f')
                duration = int(time_diff.total_seconds())

            # Add current session duration to the total
            duration += session_info['session_duration']

            # Call service API to create session
            api_req = {'session': {'id_session': id_session,
                                   'session_status': TeraSessionStatus.STATUS_COMPLETED.value,
                                   'session_duration': duration}}

            api_response = self.post_to_opentera('/api/service/sessions', api_req)

            # Send events
            stop_session_event = messages.StopSessionEvent()
            stop_session_event.session_uuid = session_info['session_uuid']
            stop_session_event.service_uuid = self.service_uuid

            for user_uuid in session_info['session_users']:
                self.send_event_message(stop_session_event, 'websocket.user.' + user_uuid + '.events')

            for participant_uuid in session_info['session_participants']:
                self.send_event_message(stop_session_event, 'websocket.participant.' + participant_uuid + '.events')

            for device_uuid in session_info['session_devices']:
                self.send_event_message(stop_session_event, 'websocket.device.' + device_uuid + '.events')

            # Remove session from list
            del self.sessions[id_session]

            # Return response
            if api_response.status_code == 200:
                session_info = api_response.json()
                if isinstance(session_info, list):
                    session_info = session_info.pop()
                return {'status': 'stopped', 'session': session_info}

            return {'status': 'error', 'error_text': gettext('Error stopping session - check server logs. ')}

        return {'status': 'error', 'error_text': gettext('No matching session to stop')}

    def manage_start_session(self, session_manage_args: dict):
        # Get "useful" arguments
        id_service = session_manage_args['id_service']
        id_creator_user = session_manage_args['id_creator_user']
        id_session_type = session_manage_args['id_session_type']
        id_session = session_manage_args['id_session']

        # Get additional "start" arguments
        parameters = session_manage_args['parameters']
        participants = session_manage_args['session_participants']
        users = session_manage_args['session_users']
        # TODO handle devices
        devices = []

        # Call service API to create session
        api_response = None
        if id_session == 0:  # New session request
            api_req = {'session': {'id_session': 0,  # New session
                                   'id_creator_user': id_creator_user,
                                   'id_session_type': id_session_type,
                                   'session_participants_uuids': participants,
                                   'session_users_uuids': users,
                                   'sessiom_devices_uuids': devices,
                                   'session_parameters': parameters}
                       }

            api_response = self.post_to_opentera('/api/service/sessions', api_req)
        else:
            api_response = self.get_from_opentera('/api/service/sessions', 'id_session=' + str(id_session) +
                                                  '&with_events=1')

        if api_response.status_code == 200:

            session_info = api_response.json()

            if isinstance(session_info, list):
                session_info = session_info.pop()

            if 'session_events' not in session_info:
                session_info['session_events'] = []

            # Create start event in session events
            from datetime import datetime
            api_req = {'session_event': {'id_session_event': 0,
                                         'id_session': session_info['id_session'],
                                         'id_session_event_type': 3,  # START session event
                                         'session_event_datetime': str(datetime.now()),
                                         'session_event_context': self.service_info['service_key']
                                         }
                       }

            api_response = self.post_to_opentera('/api/service/sessions/events', api_req)

            if api_response.status_code != 200:
                return {'status': 'error', 'error_text': gettext('Cannot create session event')}

            # Add event to list
            new_event = api_response.json()

            if isinstance(new_event, list):
                new_event = new_event.pop()
            session_info['session_events'].append(new_event)

            # Replace fields with uuids
            session_info['session_participants'] = participants
            session_info['session_users'] = users
            session_info['session_devices'] = devices

            # Add session key
            session_info['session_key'] = str(uuid.uuid4())

            # New WebRTC process with send events on this pattern
            self.subscribe_pattern_with_callback('webrtc.' + session_info['session_key'],
                                                 self.nodejs_webrtc_message_callback)

            # Start WebRTC process
            # TODO do something with parameters
            retval, process_info = self.webRTCModule.create_webrtc_session(
                session_info['session_key'], id_creator_user, users, participants, devices)

            if not retval or not process_info:
                self.unsubscribe_pattern_with_callback('webrtc.' + session_info['session_key'],
                                                       self.nodejs_webrtc_message_callback)
                return {'status': 'error', 'error_text': gettext('Cannot create process')}

            # Add URL to session_info
            session_info['session_url'] = process_info['url']

            # Keep session info for future use
            self.sessions[session_info['id_session']] = session_info

            # Return session information
            return {'status': 'started', 'session': session_info}

        else:
            return {'status': 'error', 'error_text': gettext('Cannot create session')}


if __name__ == '__main__':

    # Very first thing, log to stdout
    log.startLogging(sys.stdout)

    # Load configuration
    if not Globals.config_man.load_config('VideoRehabService.json'):
        print('Invalid config')
        exit(1)

    # Global redis client
    Globals.redis_client = RedisClient(Globals.config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
    Globals.api_device_static_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceStaticTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)
    Globals.api_participant_static_token_key = \
        Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantStaticTokenAPIKey)

    # Update Service Access information
    ServiceAccessManager.api_user_token_key = Globals.api_user_token_key
    ServiceAccessManager.api_participant_token_key = Globals.api_participant_token_key
    ServiceAccessManager.api_participant_static_token_key = Globals.api_participant_static_token_key
    ServiceAccessManager.api_device_token_key = Globals.api_device_token_key
    ServiceAccessManager.api_device_static_token_key = Globals.api_device_static_token_key
    ServiceAccessManager.config_man = Globals.config_man

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
