import redis
from libtera.ConfigManager import ConfigManager

red = None


def setup_redis(config : ConfigManager):
    print('setup_redis', config )
    global red
    red = redis.Redis(host='localhost', port=6379, db=0)
    print(red)


def get_redis():
    global red
    return red
