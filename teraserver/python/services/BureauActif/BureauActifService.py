from services.BureauActif.FlaskModule import FlaskModule
from services.BureauActif.TwistedModule import TwistedModule
from services.BureauActif.ConfigManager import ConfigManager
from modules.RedisVars import RedisVars
from libtera.redis.RedisClient import RedisClient
import services.BureauActif.Globals as Globals
from sqlalchemy.exc import OperationalError

if __name__ == '__main__':

    # Load configuration
    from services.BureauActif.Globals import config_man
    config_man.load_config('BureauActifService.ini')

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
        Globals.db_man.open(POSTGRES, True)
    except OperationalError:
        print("Unable to connect to database - please check settings in config file!")
        quit()

    Globals.db_man.create_defaults(config_man)

    # Global redis client
    Globals.redis_client = RedisClient(config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)

    # Main Flask module
    flask_module = FlaskModule(config_man)

    # Main Twisted module
    twisted_module = TwistedModule(config_man)

    # Run reactor
    twisted_module.run()

    print('BureauActifService - done!')
