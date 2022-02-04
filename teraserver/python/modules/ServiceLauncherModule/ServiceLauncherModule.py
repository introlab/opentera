from opentera.modules.BaseModule import BaseModule, ModuleNames
from opentera.config.ConfigManager import ConfigManager
from opentera.db.models.TeraService import TeraService

import os
import subprocess
import sys


class ServiceLauncherModule(BaseModule):

    def __init__(self, config: ConfigManager, system_only=False, enable_tests=False):
        BaseModule.__init__(self, ModuleNames.SERVICE_LAUNCHER_NAME.value, config)
        self.processList = []
        self.launch_system_service_only = system_only
        self.enable_tests = enable_tests

    def __del__(self):
        self.terminate_processes()

    def setup_module_pubsub(self):
        # Additional subscribe here

        # Launch all internal services
        services = TeraService.query.all()
        for service in services:
            if service.service_system:
                # print(service)
                if service.service_key != 'OpenTeraServer':
                    self.launch_service(service)
            elif service.service_enabled and not self.launch_system_service_only:
                self.launch_service(service)

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        # print('ServiceLauncherModule - Received message ', pattern, channel, message)
        pass

    def setup_rpc_interface(self):
        pass

    def launch_service(self, service: TeraService):
        print('Launching service: ', service.service_key)
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
            if self.enable_tests:
                executable_args.append('--enable_tests=1')
            working_directory = os.path.join(os.getcwd(), 'services', 'FileTransferService')
        elif service.service_key == 'BureauActif':
            path = os.path.join(os.getcwd(), 'services', 'BureauActif', 'BureauActifService.py')
            executable_args.append(path)
            working_directory = os.path.join(os.getcwd(), 'services', 'BureauActif')
        elif service.service_key == 'VideoRehabService':
            path = os.path.join(os.getcwd(), 'services', 'VideoRehabService', 'VideoRehabService.py')
            executable_args.append(path)
            working_directory = os.path.join(os.getcwd(), 'services', 'VideoRehabService')
        else:
            print('Unable to start :', service.service_key)
            self.logger.log_error(self.module_name, 'Unable to start', service.service_key)
            return

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
