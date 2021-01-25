from opentera.services.ServiceConfigManager import ServiceConfigManager
from opentera.modules.BaseModule import BaseModule

import os
import subprocess


class WebRTCModule(BaseModule):

    def __init__(self, config: ServiceConfigManager):
        BaseModule.__init__(self, config.service_config['name'] + '.WebRTCModule', config)
        self.processList = []
        self.max_sessions = self.config.webrtc_config['max_sessions']
        self.base_port = self.config.webrtc_config['local_base_port']
        self.available_ports = [port for port in range(self.base_port, self.base_port + self.max_sessions)]
        self.used_ports = []

    def setup_module_pubsub(self):
        pass

    def setup_rpc_interface(self):
        pass

    def create_webrtc_session(self, room_name, owner_uuid, users: list, participants: list, devices: list):
        # make sure we kill sessions already started with this owner_uuid or room name
        self.terminate_webrtc_session_with_owner_uuid(owner_uuid)
        self.terminate_webrtc_session_with_room_name(room_name)

        # Get next available port
        port = self.get_available_port()
        key = room_name

        print(self.module_name + ' - Should create WebRTC session with name:', room_name, port, key)

        if port:
            url_users = 'https://' + self.config.webrtc_config['hostname'] + ':' \
                        + str(self.config.webrtc_config['external_port']) \
                        + '/webrtc/' + str(port) + '/users?key=' + key

            url_participants = 'https://' + self.config.webrtc_config['hostname'] + ':' \
                               + str(self.config.webrtc_config['external_port']) \
                               + '/webrtc/' + str(port) + '/participants?key=' + key

            url_devices = 'https://' + self.config.webrtc_config['hostname'] + ':' \
                          + str(self.config.webrtc_config['external_port']) \
                          + '/webrtc/' + str(port) + '/devices?key=' + key

            if self.launch_node(port=port, key=key, owner=owner_uuid,
                                users=users, participants=participants, devices=devices):
                # Return url
                return True, {'url_users': url_users,
                              'url_participants': url_participants,
                              'url_devices': url_devices,
                              'key': key,
                              'port': port,
                              'owner': owner_uuid,
                              'users': users,
                              'participants': participants,
                              'devices': devices}
            else:
                return False, {'error': 'Process not launched.'}
        else:
            return False, {'error': 'No available port left.'}

    def stop_webrtc_session(self, room_name, *args, **kwargs):
        for process_dict in self.processList:
            if process_dict['key'] == room_name:
                if self.terminate_webrtc_session_with_room_name(room_name):
                    return True, process_dict['key']
        return False, {}

    def get_webrtc_session_status(self, room_name):
        from requests import get
        for process_dict in self.processList:
            if process_dict['key'] == room_name:
                url = 'https://' + self.config.webrtc_config['hostname'] + ':' \
                      + str(self.config.webrtc_config['external_port']) \
                      + '/webrtc/' + str(process_dict['port']) + '/status?key=' + room_name
                response = get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    return response.json()
        return None

    def terminate_webrtc_session_with_room_name(self, room_name):
        for process_dict in self.processList:
            if process_dict['key'] == room_name:

                self.logger.log_info(self.module_name, 'terminate_webrtc_session_with_room_name',  room_name,
                                     process_dict, 'pid', str(process_dict['process'].pid))

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

                self.logger.log_info(self.module_name, 'terminate_webrtc_session_with_owner_uuid',  owner_uuid,
                                     process_dict, 'pid', str(process_dict['process'].pid))

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
        print(self.module_name + ' - Received message ', pattern, channel, message)
        pass

    def get_available_port(self):
        if not self.available_ports:
            return None

        # Pop first
        port = self.available_ports.pop(0)
        self.used_ports.append(port)
        return port

    def launch_node(self, port, key, owner, users, participants, devices):
        executable_args = [self.config.webrtc_config['executable'],
                           self.config.webrtc_config['script'],
                           '--port=' + str(port),
                           '--key=' + str(key),
                           '--debug=' + str(1)]

        # stdout=os.subprocess.PIPE, stderr=os.subprocess.PIPE)
        try:
            process = subprocess.Popen(executable_args,
                                       cwd=os.path.realpath(self.config.webrtc_config['working_directory']))

            # One more process
            self.processList.append({'process': process,
                                     'port': port,
                                     'key': key,
                                     'owner': owner,
                                     'users': users,
                                     'participants': participants,
                                     'devices': devices})

            self.logger.log_info(self.module_name, 'launch_node', executable_args, 'pid', str(process.pid))

            print(self.module_name + ' - started process', process)
            return True
        except OSError as e:
            print(self.module_name + ' - error starting process:', e)

        return False

