from opentera.services.ServiceOpenTera import ServiceOpenTera
from opentera.modules.BaseModule import ModuleNames, create_module_message_topic_from_name, \
    create_module_event_topic_from_name
from opentera.db.models.TeraSession import TeraSessionStatus
from opentera.db.models.TeraSessionEvent import TeraSessionEvent

# Twisted
from twisted.internet import defer
from twisted.python import log
import opentera.messages.python as messages
import sys
import uuid
import json

from flask_babel import gettext

# Configuration
from ConfigManager import ConfigManager

from opentera.redis.RedisVars import RedisVars

# Modules
from requests import Response

# Messages
from google.protobuf.json_format import ParseError
from google.protobuf.message import DecodeError

"""
This class should be moved to opentera/service
"""


class BaseWebRTCService(ServiceOpenTera):
    def __init__(self, config_man: ConfigManager, service_info: dict):
        ServiceOpenTera.__init__(self, config_man, service_info)

        # This variable must be updated in derived classes
        self.webRTCModule = None

        # Active sessions
        self.sessions = dict()

    @defer.inlineCallbacks
    def register_to_events(self):
        # Need to register to events produced by UserManagerModule
        yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
            ModuleNames.USER_MANAGER_MODULE_NAME), self.user_manager_event_received)

        super().register_to_events()

    def send_join_message(self, session_info, join_msg: str = gettext('Join me!'), target_users: list = None,
                          target_participants: list = None, target_devices: list = None):

        self.logger.log_info(self.config['name'],
                             'send_join_message',
                             session_info['session_uuid'],
                             target_users,
                             target_participants,
                             target_devices)

        users = session_info['session_users']
        participants = session_info['session_participants']
        devices = session_info['session_devices']
        parameters = session_info['session_parameters']

        join_message = messages.JoinSessionEvent()

        # Order is important here if multiple session creator
        if session_info['id_creator_service']:
            join_message.session_creator_name = session_info['session_creator_service']
        if session_info['id_creator_device']:
            join_message.session_creator_name = session_info['session_creator_device']
        if session_info['id_creator_participant']:
            join_message.session_creator_name = session_info['session_creator_participant']
        if session_info['id_creator_user']:
            join_message.session_creator_name = session_info['session_creator_user']
        join_message.session_uuid = session_info['session_uuid']
        for user_uuid in users:
            join_message.session_users.extend([user_uuid])
        for participant_uuid in participants:
            join_message.session_participants.extend([participant_uuid])
        for device_uuid in devices:
            join_message.session_devices.extend([device_uuid])
        join_message.join_msg = join_msg
        if not parameters:
            parameters = {}

        # Conversion to str
        if type(parameters) is dict:
            parameters = json.dumps(parameters)

        join_message.session_parameters = parameters

        join_message.service_uuid = self.service_uuid

        # Send invitations (as events) for users, participants and devices
        if target_users is None:
            target_users = users
        if target_devices is None:
            target_devices = devices
        if target_participants is None:
            target_participants = participants

        for user_uuid in target_users:
            join_message.session_url = session_info['session_url_users']
            self.send_event_message(join_message, 'websocket.user.'
                                    + user_uuid + '.events')
        for participant_uuid in target_participants:
            join_message.session_url = session_info['session_url_participants']
            self.send_event_message(join_message, 'websocket.participant.'
                                    + participant_uuid + '.events')
        for device_uuid in target_devices:
            join_message.session_url = session_info['session_url_devices']
            self.send_event_message(join_message, 'websocket.device.'
                                    + device_uuid + '.events')

        # Send event to UserManager to change "busy" status
        self.send_tera_message(join_message, 'service' + self.service_info['service_key'],
                               create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))

    def user_manager_event_received(self, pattern, channel, message):
        # print('BaseWebRTCService - user_manager_event_received', pattern, channel, message)
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
            print('BaseWebRTCService - DecodeError ', pattern, channel, message, d)
        except ParseError as e:
            print('BaseWebRTCService - Failure in redisMessageReceived', e)

    def handle_user_event(self, event: messages.UserEvent):
        # print('BaseWebRTCService.handle_user_event', event)
        # Verify each session
        for id_session in self.sessions:
            session_info = self.sessions[id_session]

            # Verify if it contains the user_uuid
            if event.user_uuid in session_info['session_users']:
                # Verify the event type
                if event.type == messages.UserEvent.USER_CONNECTED:
                    # Resend invitation to newly connected user
                    # print('Resending invitation to ', event, session_info)

                    self.send_join_message(session_info=session_info, target_devices=[], target_participants=[],
                                           target_users=[event.user_uuid])

                elif event.type == messages.UserEvent.USER_DISCONNECTED:
                    # Terminate session if last user ?
                    if 'session_creator_user_uuid' in session_info:
                        if session_info['session_creator_user_uuid'] == event.user_uuid:
                            manage_session_args = {'id_session': id_session}
                            self.manage_stop_session(manage_session_args)
                            # End loop, sessions dict will be changed in manage_stop_session
                            break

    def handle_participant_event(self, event: messages.ParticipantEvent):
        # print('BaseWebRTCService.handle_participant_event', event)
        # Verify each session
        for id_session in self.sessions:
            session_info = self.sessions[id_session]

            # Verify if it contains the user_uuid
            if event.participant_uuid in session_info['session_participants']:
                # Verify the event type
                if event.type == messages.ParticipantEvent.PARTICIPANT_CONNECTED:
                    # Resend invitation to newly connected user
                    # print('Resending invitation to ', event, session_info)

                    self.send_join_message(session_info=session_info, target_devices=[],
                                           target_participants=[event.participant_uuid], target_users=[])

                elif event.type == messages.ParticipantEvent.PARTICIPANT_DISCONNECTED:
                    # End session if the participant was the creator
                    if 'session_creator_participant_uuid' in session_info:
                        if session_info['session_creator_participant_uuid'] == event.participant_uuid:
                            manage_session_args = {'id_session': id_session}
                            self.manage_stop_session(manage_session_args)
                            # End loop, sessions dict will be changed in manage_stop_session
                            break

    def handle_device_event(self, event: messages.DeviceEvent):
        # print('BaseWebRTCService.handle_device_event', event)
        # Verify each session
        for id_session in self.sessions:
            session_info = self.sessions[id_session]

            # Verify if it contains the user_uuid
            if event.device_uuid in session_info['session_devices']:
                # Verify the event type
                if event.type == messages.DeviceEvent.DEVICE_CONNECTED:
                    # Resend invitation to newly connected user
                    # print('Resending invitation to ', event, session_info)

                    self.send_join_message(session_info=session_info, target_devices=[event.device_uuid],
                                           target_participants=[], target_users=[])

                elif event.type == messages.DeviceEvent.DEVICE_DISCONNECTED:
                    # End session if the device was the creator
                    if 'session_creator_device_uuid' in session_info:
                        if session_info['session_creator_device_uuid'] == event.device_uuid:
                            manage_session_args = {'id_session': id_session}
                            self.manage_stop_session(manage_session_args)
                            # End loop, sessions dict will be changed in manage_stop_session
                            break

    def nodejs_webrtc_message_callback(self, pattern, channel, message):
        # print('WebRTCModule - nodejs_webrtc_message_callback', pattern, channel, message)
        parts = channel.split(".")
        if len(parts) == 2:
            session_key = parts[1]
            # print(session_key)
            if message == 'Ready!':
                # print('Ready!')
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
            self.send_join_message(session_info=session_info)

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

    def post_session_event(self, event_type: int, id_session: int, event_text: str = None) -> Response:
        from datetime import datetime
        api_req = {'session_event': {'id_session_event': 0,
                                     'id_session': id_session,
                                     'id_session_event_type': event_type,  # START session event
                                     'session_event_datetime': str(datetime.now()),
                                     'session_event_context': self.service_info['service_key']
                                     }
                   }

        if event_text:
            api_req['session_event']['session_event_text'] = event_text

        return self.post_to_opentera('/api/service/sessions/events', api_req)

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
                elif action == 'invite':
                    return self.manage_invite_to_session(session_manage_args)
                elif action == 'remove':
                    return self.manage_remove_from_session(session_manage_args)
                elif action == 'invite_reply':
                    return self.manage_invite_reply(session_manage_args)

        except json.JSONDecodeError as e:
            print('Error', e)
            return None

        return None

    def manage_start_session(self, session_manage_args: dict):
        # Get "useful" arguments
        id_service = session_manage_args['id_service']
        id_session_type = session_manage_args['id_session_type']
        id_session = session_manage_args['id_session']
        parameters = None
        if 'parameters' in session_manage_args:
            parameters = session_manage_args['parameters']

        # Get additional "start" arguments
        if 'session_participants' in session_manage_args:
            participants = session_manage_args['session_participants']
        else:
            participants = []
        if 'session_users' in session_manage_args:
            users = session_manage_args['session_users']
        else:
            users = []
        if 'session_devices' in session_manage_args:
            devices = session_manage_args['session_devices']
        else:
            devices = []

        # Call service API to create session
        api_response = None
        if id_session == 0:  # New session request
            api_req = {'id_session': 0,  # New session
                       'id_session_type': id_session_type,
                       'session_participants_uuids': participants,
                       'session_users_uuids': users,
                       'session_devices_uuids': devices,
                       'session_parameters': parameters
                       }
            if 'id_creator_user' in session_manage_args:
                api_req['id_creator_user'] = session_manage_args['id_creator_user']

            if 'id_creator_participant' in session_manage_args:
                api_req['id_creator_participant'] = session_manage_args['id_creator_participant']

            if 'id_creator_device' in session_manage_args:
                api_req['id_creator_device'] = session_manage_args['id_creator_device']

            if 'id_creator_service' in session_manage_args:
                api_req['id_creator_service'] = session_manage_args['id_creator_service']

            api_req = {'session': api_req}
            api_response = self.post_to_opentera('/api/service/sessions', api_req)
        else:
            api_response = self.get_from_opentera('/api/service/sessions', {'id_session': str(id_session),
                                                                            'with_events': True})

        if api_response.status_code == 200:

            session_info = api_response.json()

            if isinstance(session_info, list):
                session_info = session_info.pop()

            if 'session_events' not in session_info:
                session_info['session_events'] = []

            # Create start event in session events
            api_response = self.post_session_event(event_type=TeraSessionEvent.SessionEventTypes.SESSION_START.value
                                                   , id_session=session_info['id_session'])

            if api_response.status_code != 200:
                return {'status': 'error', 'error_text': gettext('Cannot create session event')}

            # Add event to list
            new_event = api_response.json()

            if isinstance(new_event, list):
                new_event = new_event.pop()
            session_info['session_events'].append(new_event)

            # Replace fields with uuids if presents
            session_info['session_participants'] = participants
            session_info['session_users'] = users
            session_info['session_devices'] = devices

            # Add session key
            session_info['session_key'] = str(uuid.uuid4())

            # Get session creator uuid
            creator_uuid = None
            if 'session_creator_user_uuid' in session_info:
                creator_uuid = session_info['session_creator_user_uuid']
            elif 'session_creator_participant_uuid' in session_info:
                creator_uuid = session_info['session_creator_participant_uuid']
            elif 'session_creator_device_uuid' in session_info:
                creator_uuid = session_info['session_creator_device_uuid']
            elif 'session_creator_service_uuid' in session_info:
                creator_uuid = session_info['session_creator_service_uuid']

            session_info['session_creator_uuid'] = creator_uuid

            # New WebRTC process with send events on this pattern
            self.subscribe_pattern_with_callback('webrtc.' + session_info['session_key'],
                                                 self.nodejs_webrtc_message_callback)

            # Start WebRTC process
            retval, process_info = self.webRTCModule.create_webrtc_session(session_info)

            if not retval or not process_info:
                self.unsubscribe_pattern_with_callback('webrtc.' + session_info['session_key'],
                                                       self.nodejs_webrtc_message_callback)
                return {'status': 'error', 'error_text': gettext('Cannot create process')}

            # Add URL to session_info
            session_info['session_url_users'] = process_info['url_users']
            session_info['session_url_participants'] = process_info['url_participants']
            session_info['session_url_devices'] = process_info['url_devices']

            # Keep session info for future use
            self.sessions[session_info['id_session']] = session_info

            # Return session information
            return {'status': 'started', 'session': session_info}

        else:
            return {'status': 'error', 'error_text': gettext('Cannot create session') + ': ' + api_response.text}

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
            api_response = self.post_session_event(event_type=TeraSessionEvent.SessionEventTypes.SESSION_STOP.value,
                                                   id_session=session_info['id_session'])

            if api_response.status_code != 200:
                return {'status': 'error', 'error_text': gettext('Cannot create STOP session event')}

            # Compute session duration from last start event
            from datetime import datetime
            duration = 0

            for session_event in reversed(session_info['session_events']):
                if session_event['id_session_event_type'] == 3:  # START event
                    time_diff = datetime.now() - datetime.fromisoformat(session_event['session_event_datetime']).\
                        replace(tzinfo=None)
                    duration = int(time_diff.total_seconds())
                    break

            # Default duration
            # if duration == 0:
            #     time_diff = datetime.now() - datetime.fromisoformat(session_info['session_start_datetime']).\
            #         replace(tzinfo=None)
            #     duration = int(abs(time_diff.total_seconds()))  # abs in case of sessions set in the future

            # Add current session duration to the total
            duration += session_info['session_duration']

            # Call service API to update session
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

            # Send event to UserManager to change "busy" status
            self.send_tera_message(stop_session_event, 'service' + self.service_info['service_key'],
                                   create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))

            # Remove session from list
            del self.sessions[id_session]

            # Return response
            if api_response.status_code == 200:
                session_info = api_response.json()
                if isinstance(session_info, list):
                    session_info = session_info.pop()
                return {'status': 'stopped', 'session': session_info}

            return {'status': 'error', 'error_text': gettext('Error stopping session - check server logs')}

        return {'status': 'error', 'error_text': gettext('No matching session to stop')}

    def manage_invite_to_session(self, session_manage_args: dict):
        id_session = session_manage_args['id_session']
        # id_service = session_manage_args['id_service']
        # id_creator_user = session_manage_args['id_creator_user']

        if id_session in self.sessions:
            session_info = self.sessions[id_session]

            new_session_users = []
            new_session_devices = []
            new_session_participants = []

            if 'session_users' in session_manage_args:
                new_session_users = session_manage_args['session_users']
                session_info['session_users'].extend(new_session_users)

                for session_user in new_session_users:
                    # Get names for log
                    # TODO
                    #     api_response = self.get_from_opentera('/api/service')
                    api_response = self.post_session_event(
                        event_type=TeraSessionEvent.SessionEventTypes.SESSION_JOIN.value, id_session=id_session,
                        event_text=gettext('User') + ': ' + session_user)
                    if api_response.status_code != 200:
                        return {'status': 'error', 'error_text': gettext('Error creating user invited session event')}

            if 'session_participants' in session_manage_args:
                new_session_participants = session_manage_args['session_participants']
                session_info['session_participants'].extend(new_session_participants)
                for session_participant in new_session_participants:
                    # Get names for log
                    # TODO
                    #     api_response = self.get_from_opentera('/api/service')
                    api_response = self.post_session_event(
                        event_type=TeraSessionEvent.SessionEventTypes.SESSION_JOIN.value,
                        id_session=id_session,
                        event_text=gettext('Participant') + ': ' + session_participant)
                    if api_response.status_code != 200:
                        return {'status': 'error', 'error_text': gettext('Error creating participant invited '
                                                                         'session event')}

            if 'session_devices' in session_manage_args:
                new_session_devices = session_manage_args['session_devices']
                session_info['session_devices'].extend(new_session_devices)
                for session_device in new_session_devices:
                    # Get names for log
                    # TODO
                    #     api_response = self.get_from_opentera('/api/service')
                    api_response = self.post_session_event(
                        event_type=TeraSessionEvent.SessionEventTypes.SESSION_JOIN.value,
                        id_session=id_session,
                        event_text=gettext('Device') + ': ' + session_device)
                    if api_response.status_code != 200:
                        return {'status': 'error', 'error_text': gettext('Error creating device invited '
                                                                         'session event')}

            # Update session with new invitees
            api_req = {'session': {'id_session': id_session,  # New session
                                   'session_participants_uuids': session_info['session_participants'],
                                   'session_users_uuids': session_info['session_users'],
                                   'sessiom_devices_uuids': session_info['session_devices'],
                                   }
                       }
            api_response = self.post_to_opentera('/api/service/sessions', api_req)
            if api_response.status_code == 200:
                # Resend join session message to all invitees to let them update their list if needed
                self.send_join_message(session_info=session_info)
                return {'status': 'invited', 'session': session_info}

            return {'status': 'error', 'error_text': gettext('Error updating session')}

    def manage_remove_from_session(self, session_manage_args: dict):
        id_session = session_manage_args['id_session']
        # id_service = session_manage_args['id_service']
        # id_creator_user = session_manage_args['id_creator_user']

        if id_session in self.sessions:
            session_info = self.sessions[id_session]

            removed_session_users = []
            removed_session_devices = []
            removed_session_participants = []

            session_users = session_info['session_users']
            session_devices = session_info['session_devices']
            session_participants = session_info['session_participants']

            if 'session_users' in session_manage_args:
                removed_session_users = session_manage_args['session_users']
                session_info['session_users'] = [item for item in session_info['session_users']
                                                 if item not in removed_session_users]

                for session_user in removed_session_users:
                    # Get names for log
                    # TODO
                    #     api_response = self.get_from_opentera('/api/service')
                    api_response = self.post_session_event(
                        event_type=TeraSessionEvent.SessionEventTypes.SESSION_LEAVE.value,
                        id_session=id_session,
                        event_text=gettext('User') + ': ' + session_user)
                    if api_response.status_code != 200:
                        return {'status': 'error', 'error_text': gettext('Error creating user left session event')}

            if 'session_participants' in session_manage_args:
                removed_session_participants = session_manage_args['session_participants']
                session_info['session_participants'] = [item for item in session_info['session_participants']
                                                        if item not in removed_session_participants]
                for session_participant in removed_session_participants:
                    # Get names for log
                    # TODO
                    #     api_response = self.get_from_opentera('/api/service')
                    api_response = self.post_session_event(
                        event_type=TeraSessionEvent.SessionEventTypes.SESSION_LEAVE.value,
                        id_session=id_session,
                        event_text=gettext('Participant') + ': ' + session_participant)
                    if api_response.status_code != 200:
                        return {'status': 'error', 'error_text': gettext('Error creating participant left '
                                                                         'session event')}

            if 'session_devices' in session_manage_args:
                removed_session_devices = session_manage_args['session_devices']
                session_info['session_devices'] = [item for item in session_info['session_devices']
                                                   if item not in removed_session_devices]
                for session_device in removed_session_devices:
                    # Get names for log
                    # TODO
                    #     api_response = self.get_from_opentera('/api/service')
                    api_response = self.post_session_event(
                        event_type=TeraSessionEvent.SessionEventTypes.SESSION_LEAVE.value,
                        id_session=id_session,
                        event_text=gettext('Device') + ': ' + session_device)
                    if api_response.status_code != 200:
                        return {'status': 'error', 'error_text': gettext('Error creating device left '
                                                                         'session event')}

            # Create and send leave session event message
            leave_message = messages.LeaveSessionEvent()
            leave_message.session_uuid = session_info['session_uuid']
            leave_message.service_uuid = self.service_uuid
            for user_uuid in removed_session_users:
                leave_message.leaving_users.extend([user_uuid])
            for participant_uuid in removed_session_participants:
                leave_message.leaving_participants.extend([participant_uuid])
            for device_uuid in removed_session_devices:
                leave_message.leaving_devices.extend([device_uuid])

            # Broadcast to all
            for user_uuid in session_users:
                self.send_event_message(leave_message, 'websocket.user.' + user_uuid + '.events')
            for participant_uuid in session_participants:
                self.send_event_message(leave_message, 'websocket.participant.' + participant_uuid + '.events')
            for device_uuid in session_devices:
                self.send_event_message(leave_message, 'websocket.device.' + device_uuid + '.events')

            # Send event to UserManager to change "busy" status
            self.send_tera_message(leave_message, 'service' + self.service_info['service_key'],
                                   create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))

            # Don't update session with current list of users - participants... We need to keep a trace that they
            # were part of that session at some point!

            return {'status': 'removed', 'session': session_info}

    def manage_invite_reply(self, session_manage_args: dict):
        id_session = session_manage_args['id_session']
        parameters = session_manage_args['parameters']
        reply_code = parameters['reply_code']

        if id_session in self.sessions:
            session_info = self.sessions[id_session]

            join_session_reply = messages.JoinSessionReplyEvent()
            join_session_reply.session_uuid = session_info['session_uuid']
            join_session_reply.join_reply = parameters['reply_code']
            if 'reply_msg' in parameters:
                join_session_reply.reply_msg = parameters['reply_msg']
            if 'user_uuid' in parameters:
                join_session_reply.user_uuid = parameters['user_uuid']
                if parameters['reply_code'] != messages.JoinSessionReplyEvent.REPLY_ACCEPTED:
                    session_info['session_users'] = [item for item in session_info['session_users']
                                                     if item != parameters['user_uuid']]
                    # Create session join refused event
                    # TODO: Get user name instead of user uuid
                    api_response = self.post_session_event(
                        event_type=TeraSessionEvent.SessionEventTypes.SESSION_JOIN_REFUSED.value,
                        id_session=session_info['id_session'],
                        event_text=gettext('User') + ' ' + parameters['user_uuid'])

                    if api_response.status_code != 200:
                        return {'status': 'error', 'error_text': gettext('Cannot create refused session event')}

            if 'participant_uuid' in parameters:
                join_session_reply.participant_uuid = parameters['participant_uuid']
                if parameters['reply_code'] != messages.JoinSessionReplyEvent.REPLY_ACCEPTED:
                    session_info['session_participants'] = [item for item in session_info['session_participants']
                                                            if item != parameters['participant_uuid']]
                    # Create session join refused event
                    # TODO: Get  participant name instead of uuid
                    api_response = self.post_session_event(
                        event_type=TeraSessionEvent.SessionEventTypes.SESSION_JOIN_REFUSED.value,
                        id_session=session_info['id_session'],
                        event_text=gettext('Participant') + ' ' + parameters['participant_uuid'])

                    if api_response.status_code != 200:
                        return {'status': 'error', 'error_text': gettext('Cannot create refused session event')}

            if 'device_uuid' in parameters:
                join_session_reply.device_uuid = parameters['device_uuid']
                if parameters['reply_code'] != messages.JoinSessionReplyEvent.REPLY_ACCEPTED:
                    session_info['session_devices'] = [item for item in session_info['session_devices']
                                                       if item != parameters['device_uuid']]
                    # Create session join refused event
                    # TODO: Get device name instead of uuid
                    api_response = self.post_session_event(
                        event_type=TeraSessionEvent.SessionEventTypes.SESSION_JOIN_REFUSED.value,
                        id_session=session_info['id_session'],
                        event_text=gettext('Device') + ' ' + parameters['device_uuid'])

                    if api_response.status_code != 200:
                        return {'status': 'error', 'error_text': gettext('Cannot create refused session event')}

            # Send reply message to everyone
            session_users = session_info['session_users']
            session_devices = session_info['session_devices']
            session_participants = session_info['session_participants']
            for user_uuid in session_users:
                self.send_event_message(join_session_reply, 'websocket.user.' + user_uuid + '.events')
            for participant_uuid in session_participants:
                self.send_event_message(join_session_reply, 'websocket.participant.' + participant_uuid + '.events')
            for device_uuid in session_devices:
                self.send_event_message(join_session_reply, 'websocket.device.' + device_uuid + '.events')

            # Send event to UserManager to change "busy" status
            self.send_tera_message(join_session_reply, 'service' + self.service_info['service_key'],
                                   create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))

            return {'status': 'OK', 'session': session_info}


