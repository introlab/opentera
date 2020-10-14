from services.BureauActif.FlaskModule import FlaskModule, flask_app
from services.BureauActif.TwistedModule import TwistedModule
from services.BureauActif.ConfigManager import ConfigManager
from modules.RedisVars import RedisVars
from libtera.redis.RedisClient import RedisClient
import services.BureauActif.Globals as Globals
from sqlalchemy.exc import OperationalError
from services.shared.ServiceOpenTera import ServiceOpenTera

import os


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

    def notify_service_messages(self, pattern, channel, message):
        pass

    def setup_rpc_interface(self):
        # TODO Update rpc interface
        pass


if __name__ == '__main__':

    # Load configuration
    from services.BureauActif.Globals import config_man
    config_man.load_config('BureauActifService.json')

    # Verify file upload path, create if does not exist
    verify_file_upload_directory(config_man, True)

    # DATABASE CONFIG AND OPENING
    #############################
    POSTGRES = {
        'user': config_man.db_config['username'],
        'pw': config_man.db_config['password'],
        'db': config_man.db_config['name'],
        'host': config_man.db_config['url'],
        'port': config_man.db_config['port']
    }

    try:
        Globals.db_man.open(POSTGRES, config_man.service_config['debug_mode'])
    except OperationalError as e:
        print("Unable to connect to database - please check settings in config file!", e)
        quit()

    with flask_app.app_context():
        Globals.db_man.create_defaults(config_man)

    # Global redis client
    Globals.redis_client = RedisClient(config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)

    # Get service UUID
    service_info = Globals.redis_client.redisGet(RedisVars.RedisVar_ServicePrefixKey + config_man.service_config['name'])
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

    config_man.service_config['ServiceUUID'] = service_info['service_uuid']

    # Creates communication interface with OpenTera
    Globals.service_opentera = ServiceBureauActif(config_man, service_info)

    # TODO: Set port from service config from server?

    # Main Flask module
    flask_module = FlaskModule(config_man)

    # Clean orphaned raw data files
    from services.BureauActif.libbureauactif.db.models.BureauActifData import BureauActifData
    BureauActifData.delete_orphaned_files()

    # Main Twisted module
    twisted_module = TwistedModule(config_man)

    # Run reactor
    twisted_module.run()

    print('BureauActifService - done!')
