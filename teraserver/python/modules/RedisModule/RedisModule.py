import redis
from libtera.ConfigManager import ConfigManager

red = None


def setup_redis2(config: ConfigManager):
    print('setup_redis', config)
    global red
    # For now we are not using username, password
    red = redis.Redis(host=config.redis_config['hostname'],
                      port=config.redis_config['port'],
                      db=config.redis_config['db'])
    print(red)


def get_redis2():
    global red
    return red
