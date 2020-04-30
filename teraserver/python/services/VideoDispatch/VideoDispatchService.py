from services.VideoDispatch.FlaskModule import FlaskModule
from services.VideoDispatch.TwistedModule import TwistedModule
from services.VideoDispatch.WebRTCModule import WebRTCModule
from services.VideoDispatch.OnlineUsersModule import OnlineUsersModule
from services.VideoDispatch.ConfigManager import ConfigManager
from modules.RedisVars import RedisVars
from libtera.redis.RedisClient import RedisClient
import services.VideoDispatch.Globals as Globals
import os, sys
from sqlalchemy.exc import OperationalError

if __name__ == '__main__':

    # Load configuration
    from services.VideoDispatch.Globals import config_man

    # SERVER CONFIG
    ###############
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the pyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    config_file = None

    # Set environment variable for reading configuration file
    # Will be helpful for docker containers
    if os.environ.__contains__('VIDEODISPATCH_CONFIG_PATH'):
        config_file = str(os.environ['VIDEODISPATCH_CONFIG_PATH'])
    else:
        config_file = application_path + os.sep + 'VideoDispatchService.ini'

    print("Opening config file: ", config_file)

    config_man.load_config(config_file)

    # DATABASE CONFIG AND OPENING
    #############################
    # UNUSED FOR NOW

    # POSTGRES = {
    #     'user': config_man.db_config['username'],
    #     'pw': config_man.db_config['password'],
    #     'db': config_man.db_config['name'],
    #     'host': config_man.db_config['url'],
    #     'port': config_man.db_config['port']
    # }
    #
    # try:
    #     Globals.db_man.open(POSTGRES, True)
    # except OperationalError:
    #     print("Unable to connect to database - please check settings in config file!")
    #     quit()

    # Global redis client
    Globals.redis_client = RedisClient(config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)

    # Get service UUID
    service_info = Globals.redis_client.redisGet(RedisVars.RedisVar_ServicePrefixKey + config_man.server_config['name'])
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

    config_man.server_config['ServiceUUID'] = service_info['service_uuid']

    # OnlineUsers Module
    Globals.OnlineUsers_module = OnlineUsersModule(config_man)

    # Main Flask module
    Globals.Flask_module = FlaskModule(config_man)

    # Main Twisted module
    Globals.Twisted_module = TwistedModule(config_man)

    # Main WebRTC module
    Globals.WebRTC_module = WebRTCModule(config_man)

    # Run reactor
    Globals.Twisted_module.run()

    print('VideoDispatchService - done!')
