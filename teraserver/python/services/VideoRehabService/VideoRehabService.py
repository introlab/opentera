import services.VideoRehabService.Globals as Globals
from opentera.services.modules.WebRTCModule import WebRTCModule
from opentera.redis.RedisClient import RedisClient
from opentera.db.models.TeraSession import TeraSessionStatus
from services.VideoRehabService.ConfigManager import ConfigManager
from opentera.services.ServiceAccessManager import ServiceAccessManager
from opentera.redis.RedisVars import RedisVars
from opentera.modules.BaseModule import ModuleNames, create_module_message_topic_from_name, create_module_event_topic_from_name
from google.protobuf.json_format import ParseError
from google.protobuf.message import DecodeError
from requests import Response

# Twisted
from twisted.internet import reactor, defer
from twisted.python import log
import opentera.messages.python as messages
import sys
import uuid

# Flask Module
from services.VideoRehabService.FlaskModule import FlaskModule
from opentera.services.BaseWebRTCService import BaseWebRTCService
from flask_babel import gettext


class VideoRehabService(BaseWebRTCService):
    def __init__(self, config_man: ConfigManager, this_service_info):
        BaseWebRTCService.__init__(self, config_man, this_service_info)

        # Create REST backend
        self.flaskModule = FlaskModule(Globals.config_man)

        # Create twisted service
        self.flaskModuleService = self.flaskModule.create_service()

        # Create WebRTCModule
        self.webRTCModule = WebRTCModule(config_man)

    def setup_rpc_interface(self):
        super().setup_rpc_interface()
        # TODO ADD more rpc interface here

    def notify_service_messages(self, pattern, channel, message):
        pass


if __name__ == '__main__':

    # Very first thing, log to stdout
    log.startLogging(sys.stdout)

    # Load configuration
    if not Globals.config_man.load_config('VideoRehabService.json'):
        print('Invalid config')
        exit(1)

    # Global redis client
    # Globals.redis_client = RedisClient(Globals.config_man.redis_config)
    # Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    # Globals.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
    # Globals.api_device_static_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceStaticTokenAPIKey)
    # Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)
    # Globals.api_participant_static_token_key = \
    #     Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantStaticTokenAPIKey)

    # Update Service Access information
    # ServiceAccessManager.api_user_token_key = Globals.api_user_token_key
    # ServiceAccessManager.api_participant_token_key = Globals.api_participant_token_key
    # ServiceAccessManager.api_participant_static_token_key = Globals.api_participant_static_token_key
    # ServiceAccessManager.api_device_token_key = Globals.api_device_token_key
    # ServiceAccessManager.api_device_static_token_key = Globals.api_device_static_token_key
    # ServiceAccessManager.config_man = Globals.config_man

    # Get service UUID
    redis_client = RedisClient(Globals.config_man.redis_config)
    service_info = redis_client.redisGet(RedisVars.RedisVar_ServicePrefixKey +
                                         Globals.config_man.service_config['name'])
    redis_client = None

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
