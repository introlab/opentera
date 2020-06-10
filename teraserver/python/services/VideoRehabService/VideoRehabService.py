import services.VideoRehabService.Globals as Globals
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

    def notify_service_messages(self, pattern, channel, message):
        pass

    def setup_rpc_interface(self):
        # TODO Update rpc interface
        self.rpc_api['session_manage'] = {'args': ['str:json_info'],
                                          'returns': 'dict',
                                          'callback': self.session_manage}

    def session_manage(self, json_str):
        import json
        session_manage = json.loads(json_str)
        return session_manage


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
