from opentera.modules.BaseModule import BaseModule, ModuleNames, create_module_event_topic_from_name
from opentera.config.ConfigManager import ConfigManager
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServerSettings import TeraServerSettings
import opentera.messages.python as messages
from twisted.internet import defer
import os
import subprocess
import sys
import json
from google.protobuf.json_format import ParseError
from google.protobuf.message import DecodeError
from opentera.redis.RedisVars import RedisVars


class ServiceLauncherModule(BaseModule):

    def __init__(self, config: ConfigManager, system_only=False, enable_tests=False):
        BaseModule.__init__(self, ModuleNames.SERVICE_LAUNCHER_NAME.value, config)
        self.processList = []
        self.launch_system_service_only = system_only
        self.enable_tests = enable_tests
        self.update_redis_all_service_info()

    def __del__(self):
        self.terminate_processes()

    def update_specific_service_info(self, service_key: str, service_info: dict):
        self.redisSet(RedisVars.RedisVar_ServicePrefixKey + service_key, json.dumps(service_info))

    def delete_specific_service_info(self, service_key: str):
        self.redisDelete(RedisVars.RedisVar_ServicePrefixKey + service_key)

    def update_redis_all_service_info(self):
        services = TeraService.query.all()
        for service in services:
            # Ignore special service TeraServer
            if service.service_key == 'OpenTeraServer':
                continue
            if service.service_enabled:
                self.update_specific_service_info(service.service_key, service.to_json())

    @defer.inlineCallbacks
    def setup_module_pubsub(self):
        # Additional subscribe here
        print('ServiceLauncherModule - Registering to events...')
        # Always register to user events
        yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
            ModuleNames.DATABASE_MODULE_NAME, 'service'), self.database_event_received)
        yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
            ModuleNames.DATABASE_MODULE_NAME, 'server_settings'), self.database_event_received)

        # Launch all internal services
        services = TeraService.query.all()
        for service in services:
            if service.service_system:
                # print(service)
                if service.service_key != 'OpenTeraServer':  # and service.service_key != 'LoggingService':
                    self.launch_service(service)
            elif service.service_enabled and not self.launch_system_service_only:
                # or service.service_key == 'FileTransferService'):
                self.launch_service(service)

        # Need to register to events (base class)
        super().setup_module_pubsub()

    def database_event_received(self, pattern, channel, message):
        # Process database event
        try:
            tera_event = messages.TeraEvent()
            if isinstance(message, str):
                ret = tera_event.ParseFromString(message.encode('utf-8'))
            elif isinstance(message, bytes):
                ret = tera_event.ParseFromString(message)

            database_event = messages.DatabaseEvent()

            # Look for DatabaseEvent
            for any_msg in tera_event.events:
                if any_msg.Unpack(database_event):
                    if database_event.object_type == 'service':
                        # Process event
                        try:
                            service_dict = json.loads(database_event.object_value)

                            if database_event.type == database_event.DB_CREATE or \
                                    database_event.type == database_event.DB_UPDATE:
                                # Update redis values
                                if 'id_service' in service_dict:
                                    if service_dict['service_enabled'] and 'deleted_at' not in service_dict:
                                        self.update_specific_service_info(service_dict['service_key'], service_dict)
                                    else:
                                        self.delete_specific_service_info(service_dict['service_key'])
                            elif database_event.type == database_event.DB_DELETE:
                                if 'service_key' in service_dict:
                                    self.delete_specific_service_info(service_dict['service_key'])

                        except json.JSONDecodeError as json_decode_error:
                            print('ServiceLauncherModule:database_event_received service - JSONDecodeError ',
                                  str(database_event.object_value), str(json_decode_error))
                    if database_event.object_type == 'server_settings':
                        try:
                            settings_dict = json.loads(database_event.object_value)
                            if database_event.type == database_event.DB_CREATE or \
                                    database_event.type == database_event.DB_UPDATE:
                                if settings_dict['server_settings_name'] == TeraServerSettings.ServerDeviceTokenKey:
                                    self.redisSet(RedisVars.RedisVar_DeviceStaticTokenAPIKey,
                                                  settings_dict['server_settings_value'])
                                if (settings_dict['server_settings_name'] ==
                                        TeraServerSettings.ServerParticipantTokenKey):
                                    self.redisSet(RedisVars.RedisVar_ParticipantStaticTokenAPIKey,
                                                  settings_dict['server_settings_value'])
                        except json.JSONDecodeError as json_decode_error:
                            print('ServiceLauncherModule:database_event_received server settings - JSONDecodeError ',
                                  str(database_event.object_value), str(json_decode_error))

        except DecodeError as decode_error:
            print('ServiceLauncherModule:database_event_received - DecodeError ', pattern, channel, message,
                  decode_error)
        except ParseError as parse_error:
            print('ServiceLauncherModule:database_event_received - Failure in database_event_received',
                  parse_error)

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        # print('ServiceLauncherModule - Received message ', pattern, channel, message)
        pass

    def setup_rpc_interface(self):
        pass

    def launch_service(self, service: TeraService):
        print('ServiceLauncherModule:launch_service : ', service.service_key)
        self.logger.log_info(self.module_name, 'Launching service', service.service_key)
        # First argument will be python executable
        executable_args = [sys.executable]
        working_directory = os.getcwd()
        # TODO Hardcoded paths for service right now
        if service.service_key == 'LoggingService':
            path = os.path.join(os.getcwd(), 'services', 'LoggingService', 'LoggingService.py')
            executable_args.append(path)
            working_directory = os.path.join(os.getcwd(), 'services', 'LoggingService')
        elif service.service_key == 'FileTransferService':
            path = os.path.join(os.getcwd(), 'services', 'FileTransferService', 'FileTransferService.py')
            executable_args.append(path)
            working_directory = os.path.join(os.getcwd(), 'services', 'FileTransferService')
        elif service.service_key == 'EmailService':
            path = os.path.join(os.getcwd(), 'services', 'EmailService', 'EmailService.py')
            executable_args.append(path)
            working_directory = os.path.join(os.getcwd(), 'services', 'EmailService')
        elif service.service_key == 'VideoRehabService':
            path = os.path.join(os.getcwd(), 'services', 'VideoRehabService', 'VideoRehabService.py')
            executable_args.append(path)
            working_directory = os.path.join(os.getcwd(), 'services', 'VideoRehabService')
        else:
            print('Unable to start :', service.service_key)
            self.logger.log_error(self.module_name, 'Unable to start', service.service_key)
            return

        # Append test mode argument to all launched services
        if self.enable_tests:
            executable_args.append('--enable_tests=1')

        # Start process
        process = subprocess.Popen(executable_args, cwd=os.path.realpath(working_directory))
        process_dict = {
            'process': process,
            'service': service.to_json()
        }
        self.processList.append(process_dict)
        self.logger.log_info(self.module_name, 'service started', process_dict)
        print('ServiceLauncherModule.launch_service, service started:', process_dict)

    def terminate_processes(self):
        for process in self.processList:
            process['process'].terminate()
        self.processList = []
