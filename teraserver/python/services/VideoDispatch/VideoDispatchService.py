from services.VideoDispatch.FlaskModule import FlaskModule
from services.VideoDispatch.TwistedModule import TwistedModule
from services.VideoDispatch.WebRTCModule import WebRTCModule
from services.VideoDispatch.OnlineUsersModule import OnlineUsersModule
from services.VideoDispatch.ConfigManager import ConfigManager
from modules.RedisVars import RedisVars
from libtera.redis.RedisClient import RedisClient
import services.VideoDispatch.Globals as Globals
from sqlalchemy.exc import OperationalError

if __name__ == '__main__':

    # Load configuration
    from services.VideoDispatch.Globals import config_man
    config_man.load_config('VideoDispatchService.ini')

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
