from modules.RedisModule.RedisModule import get_redis
from flask import jsonify

from libtera.redis.RedisClient import RedisClient

from libtera.ConfigManager import ConfigManager


class OnlineUserRegistry:
    def __init__(self):
        self.user_list = list()

    def user_online(self, uuid):
        print('user_online: ', uuid)
        if not self.user_list.__contains__(uuid):
            self.user_list.append(uuid)

    def user_offline(self, uuid):
        print('user_offline', uuid)
        if self.user_list.__contains__(uuid):
            self.user_list.remove(uuid)

    def online_users(self):
        return self.user_list


# Will use twisted Async Redis client
class UserManagerModule(RedisClient):
    def __init__(self, config: ConfigManager):
        self.redis_config = config.redis_config
        super().__init__(config=self.redis_config)
        self.registry = OnlineUserRegistry()

    def setup(self):
        pass

    def redisConnectionMade(self):
        print('UserManagerModule.connectionMade')
        self.subscribe('websocket.*')

    def handle_websocket_messages(self, uuid, message):
        print('handle_websocket_messages', uuid, message)
        if message == b'connected' or message == 'connected':
            self.registry.user_online(uuid)
            return True
        if message == b'disconnected' or message == 'disconnected':
            self.registry.user_offline(uuid)
            return True
        if message == b'list' or message == 'list':
            online_users = str(self.registry.online_users())
            # Answer
            print('answering', 'server.' + str(uuid) + '.answer', online_users)
            get_redis().publish('server.' + str(uuid) + '.answer', online_users)
            return True

        print('Error unhandled message ', uuid, message)
        return False

    def redisMessageReceived(self, pattern, channel, message):
        print('UserManagerModule message received', pattern, channel, message)
        parts = channel.split('.')
        if 'websocket' in parts[0]:
            self.handle_websocket_messages(parts[1], message)



