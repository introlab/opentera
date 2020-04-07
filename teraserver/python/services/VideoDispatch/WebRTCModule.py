from services.VideoDispatch.ConfigManager import ConfigManager
from messages.python.CreateSession_pb2 import CreateSession
from modules.BaseModule import BaseModule, ModuleNames

import os
import subprocess
import threading
import sys


class WebRTCModule(BaseModule):

    def __init__(self, config: ConfigManager):
        BaseModule.__init__(self, "VideoDispatchService.WebRTCModule", config)
        self.processList = []
        self.max_sessions = self.config.webrtc_config['max_sessions']
        self.base_port = self.config.webrtc_config['local_base_port']
        self.available_ports = [port for port in range(self.base_port, self.base_port + self.max_sessions)]
        self.used_ports = []

    def __del__(self):
        # self.unsubscribe_pattern_with_callback("webrtc.*", self.webrtc_message_callback_deprecated)
        pass

    def setup_module_pubsub(self):
        # Additional subscribe
        # TODO change those messages to use complete protobuf messaging system
        # self.subscribe_pattern_with_callback("webrtc.*", self.webrtc_message_callback_deprecated)
        pass

    def setup_rpc_interface(self):
        self.rpc_api['create_session'] = {'args': ['str:room_name', 'str:owner_uuid'],
                                          'returns': 'dict',
                                          'callback': self.create_webrtc_session}

        self.rpc_api['stop_session'] = {'args': ['str:room_name'],
                                        'returns': 'dict',
                                        'callback': self.stop_webrtc_session}

    def create_webrtc_session(self, room_name, owner_uuid, *args, **kwargs):

        # make sure we kill sessions already started with this owner_uuid or room name
        self.terminate_webrtc_session_with_owner_uuid(owner_uuid)
        self.terminate_webrtc_session_with_room_name(room_name)

        # Participants are listed in args
        participant_list = []
        for participant in args:
            participant_list.append(participant)

        # Get next available port
        port = self.get_available_port()
        key = room_name

        print('WebRTCModule - Should create WebRTC session with name:', room_name, port, key)

        if port:
            url = 'https://' + self.config.webrtc_config['hostname'] + ':' \
                  + str(self.config.webrtc_config['external_port']) \
                  + '/teraplus/' + str(port) + '/teraplus?key=' + key

            if self.launch_node(port=port, key=key, owner=owner_uuid, participants=participant_list):
                # Return url
                return {'url': url, 'key': key, 'port': port, 'owner': owner_uuid, 'participants': participant_list}
            else:
                return {'error': 'Process not launched.'}
        else:
            return {'error': 'No available port left.'}

    def stop_webrtc_session(self, room_name, *args, **kwargs):
        for process_dict in self.processList:
            if process_dict['key'] == room_name:
                participants = process_dict['participants']
                owner = process_dict['owner']
                if self.terminate_webrtc_session_with_room_name(room_name):
                    return {'participants': participants, 'owner': owner}
        return {}

    def terminate_webrtc_session_with_room_name(self, room_name):
        for process_dict in self.processList:
            if process_dict['key'] == room_name:
                # Terminate process
                process_dict['process'].kill()
                # Wait for process return
                process_dict['process'].wait()

                # Remove from process list
                self.processList.remove(process_dict)

                # Remove from used ports
                self.used_ports.remove(process_dict['port'])

                # Add to available ports
                self.available_ports.append(process_dict['port'])

                return True
        return False

    def terminate_webrtc_session_with_owner_uuid(self, owner_uuid):
        for process_dict in self.processList:
            if process_dict['owner'] == owner_uuid:
                # Terminate process
                process_dict['process'].kill()
                # Wait for process return
                process_dict['process'].wait()

                # Remove from process list
                self.processList.remove(process_dict)

                # Remove from used ports
                self.used_ports.remove(process_dict['port'])

                # Add to available ports
                self.available_ports.append(process_dict['port'])

                return True
        return False

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('WebRTCModule - Received message ', pattern, channel, message)
        pass

    def get_available_port(self):
        if not self.available_ports:
            return None

        # Pop first
        port = self.available_ports.pop(0)
        self.used_ports.append(port)
        return port

    def launch_node(self, port, key, owner, participants):
        executable_args = [self.config.webrtc_config['executable'],
                           self.config.webrtc_config['script'],
                           str(port),
                           str(key)]

        # stdout=os.subprocess.PIPE, stderr=os.subprocess.PIPE)
        try:
            process = subprocess.Popen(executable_args,
                                       cwd=os.path.realpath(self.config.webrtc_config['working_directory']))

            # One more process
            self.processList.append({'process': process,
                                     'port': port,
                                     'key': key,
                                     'owner': owner,
                                     'participants': participants})

            print('WebRTCModule - started process', process)
            return True
        except OSError as e:
            print('WebRTCModule - error starting process:', e)

        return False

