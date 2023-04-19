import services.VideoRehabService.Globals as Globals
from opentera.services.modules.WebRTCModule import WebRTCModule
from opentera.redis.RedisClient import RedisClient
from services.VideoRehabService.ConfigManager import ConfigManager
from opentera.redis.RedisVars import RedisVars
from opentera.forms.TeraForm import TeraForm, TeraFormSection, TeraFormItem

# Twisted
from twisted.internet import reactor
from twisted.python import log
import sys

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

    # Override from ServiceOpenTera
    def get_session_type_config_form(self, id_session_type: int) -> dict:
        # Sections
        form = TeraForm("session_type_config")

        section = TeraFormSection("general", gettext("General configuration"))
        form.add_section(section)
        # Items
        section.add_item(TeraFormItem("session_recordable", gettext("Allow session recording"),
                                      "boolean", False, item_default=False))

        return form.to_dict()


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
