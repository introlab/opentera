from libtera.redis.RedisProtocolFactory import RedisProtocolFactory, redisProtocol

# Twisted
from twisted.application import internet, service
from twisted.internet import reactor, ssl, defer

# Event based, twisted redis
import txredisapi as txredis

# Blocking redis
import redis


class RedisClient:

    def __init__(self, config=None):
        print('Init RedisClient', self, config)
        self.protocol = None
        self.callbacks_dict = dict()
        # self.redisConfig = config

        # Fill config
        if config is None:
            print('RedisClient - Warning, using default redis configuration')
            config = {'hostname': 'localhost', 'port': 6379, 'db': 0}

        # Redis client (synchronous)
        self.redis = redis.Redis(host=config['hostname'], port=config['port'], db=config['db'])

        # Redis client (async)
        reactor.connectTCP(config['hostname'], config['port'], RedisProtocolFactory(parent=self, protocol=redisProtocol))

    def redisConnectionMade(self):
        print('RedisClient connectionMade')
        pass

    def redisMessageReceived(self, pattern, channel, message):
        print(self, 'redisMessageReceived', pattern, channel, message)
        if pattern in self.callbacks_dict:
            # Call function.
            self.callbacks_dict[pattern](pattern, channel, message)

    def redisConnectionLost(self, reason):
        print("RedisClient lost connection", reason)
        pass

    def setProtocol(self, protocol: redisProtocol):
        print('RedisClient set protocol', protocol)
        self.protocol = protocol

    def subscribe(self, topic):
        if self.protocol:
            print('RedisClient (', self, ') subscribing to: ',  topic)
            ret = self.protocol.psubscribe(topic)
        else:
            print('Error, no protocol')

    def unsubscribe(self, topic):
        if self.protocol:
            self.protocol.punsubscribe(topic)

    def publish(self, topic, message):
        self.redis.publish(topic, message)

    def redisGet(self, key):
        return self.redis.get(key)

    def redisSet(self, key, value, ex=None):
        self.redis.set(key, value, ex=ex)

    def redisDelete(self, key):
        self.redis.delete(key)

    def subscribe_pattern_with_callback(self, pattern, function):
        print(self, 'subscribe_pattern_with_callback', pattern, function)
        self.callbacks_dict[pattern] = function
        self.subscribe(pattern)

    def unsubscribe_pattern_with_callback(self, pattern, function):
        print(self, 'unsubscribe_pattern_with_callback', pattern, function)
        self.unsubscribe(pattern)
        del self.callbacks_dict[pattern]


# Debug
if __name__ == '__main__':
    print('Starting')

    class MyClient(RedisClient):
        def redisConnectionMade(self):
            self.subscribe('*')

    client = MyClient()

    print('setting variable')

    client.redisSet('papa', 'rien', ex=60)

    print('redis get', client.redisGet('papa'))

    print('Starting reactor')
    reactor.run()



