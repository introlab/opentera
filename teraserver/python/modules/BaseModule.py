from libtera.redis.RedisClient import RedisClient
from libtera.ConfigManager import ConfigManager


class BaseModule(RedisClient):
    def __init__(self, config: ConfigManager):
        self.module_name = None
        # Init redis with configuration
        RedisClient.__init__(self, config=config.redis_config)

