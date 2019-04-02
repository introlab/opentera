from libtera.redis.RedisClient import RedisClient
from libtera.ConfigManager import ConfigManager


# Will use twisted Async Redis client
class WebRTCModule(RedisClient):

    def __init__(self, config: ConfigManager):
        self.config = config
        RedisClient.__init__(self, config=self.config.redis_config)

    def redisConnectionMade(self):
        print('WebRTCModule.redisConnectionMade')
        self.subscribe('webrtc.*')

    def redisMessageReceived(self, pattern, channel, message):
        print('WebRTCModule message received', pattern, channel, message)
        parts = channel.split('.')
        if 'webrtc' in parts[0]:
            print(self, ' - should handle webrtc message')

