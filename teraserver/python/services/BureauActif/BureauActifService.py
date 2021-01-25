import services.BureauActif.Globals as Globals
from services.BureauActif.ConfigManager import ConfigManager

from opentera.redis.RedisVars import RedisVars

from opentera.redis.RedisClient import RedisClient

from sqlalchemy.exc import OperationalError

from opentera.services.ServiceAccessManager import ServiceAccessManager

# Twisted
from twisted.internet import reactor
from twisted.python import log

# Flask Module
from services.BureauActif.FlaskModule import FlaskModule, flask_app
from opentera.services.ServiceOpenTera import ServiceOpenTera

import os
import sys


def verify_file_upload_directory(config: ConfigManager, create=True):
    file_upload_path = config.service_config['upload_path']

    if not os.path.exists(file_upload_path):
        if create:
            # TODO Change permissions?
            os.mkdir(file_upload_path, 0o700)
        else:
            return None
    return file_upload_path


class ServiceBureauActif(ServiceOpenTera):
    def __init__(self, config_man: ConfigManager, this_service_info):
        ServiceOpenTera.__init__(self, config_man, this_service_info)

        # Create REST backend
        self.flaskModule = FlaskModule(Globals.config_man)

        # Create twisted service
        self.flaskModuleService = self.flaskModule.create_service()

    def notify_service_messages(self, pattern, channel, message):
        pass

    def setup_rpc_interface(self):
        # TODO Update rpc interface
        pass


if __name__ == '__main__':

    # Very first thing, log to stdout
    log.startLogging(sys.stdout)

    # Load configuration
    if not Globals.config_man.load_config('BureauActifService.json'):
        print('Invalid config')
        exit(1)

    # Verify file upload path, create if does not exist
    verify_file_upload_directory(Globals.config_man, True)

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

    # DATABASE CONFIG AND OPENING
    #############################
    POSTGRES = {
        'user': Globals.config_man.db_config['username'],
        'pw':   Globals.config_man.db_config['password'],
        'db':   Globals.config_man.db_config['name'],
        'host': Globals.config_man.db_config['url'],
        'port': Globals.config_man.db_config['port']
    }

    try:
        Globals.db_man.open(POSTGRES, Globals.config_man.service_config['debug_mode'])
    except OperationalError as e:
        print("Unable to connect to database - please check settings in config file!", e)
        quit()

    with flask_app.app_context():
        Globals.db_man.create_defaults(Globals.config_man)

    # Creates communication interface with OpenTera
    # Globals.service_opentera = ServiceBureauActif(Globals.config_man, service_info)
    #
    # # Main Flask module
    # flask_module = FlaskModule(config_man)

    # Create the Service
    Globals.service = ServiceBureauActif(Globals.config_man, service_info)

    # Clean orphaned raw data files
    from services.BureauActif.libbureauactif.db.models.BureauActifData import BureauActifData
    BureauActifData.delete_orphaned_files()

    # Start App / reactor events
    reactor.run()

    # # Main Twisted module
    # twisted_module = TwistedModule(config_man)
    #
    # # Run reactor
    # twisted_module.run()
    #
    # print('BureauActifService - done!')
