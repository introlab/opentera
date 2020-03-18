from services.VideoDispatch.FlaskModule import FlaskModule
from services.VideoDispatch.TwistedModule import TwistedModule
from services.VideoDispatch.WebRTCModule import WebRTCModule
from services.VideoDispatch.ConfigManager import ConfigManager
from modules.Globals import TeraServerConstants
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
    Globals.api_user_token_key = Globals.redis_client.redisGet(TeraServerConstants.RedisVar_UserTokenAPIKey)

    # Main Flask module
    flask_module = FlaskModule(config_man)

    # Main Twisted module
    twisted_module = TwistedModule(config_man)

    # Main WebRTC module
    webrtc_module = WebRTCModule(config_man)

    # Run reactor
    twisted_module.run()

    print('VideoDispatchService - done!')
