from libtera.redis.RedisClient import RedisClient
import threading
from twisted.internet import defer


class AsyncRedisSubscribeWait:
    def __init__(self, pattern, client: RedisClient):
        self.event = threading.Event()
        self.pattern = pattern
        self.client = client
        self.answer = (None, None, None)
        self.deferred = defer.Deferred()

    def __del__(self):
        # self.stop()
        pass

    def _internal_callback(self, *args):
        print('_test_callback')
        return args

    def pattern_callback(self, pattern, channel, data):
        print(self, 'pattern_callback', pattern, channel, data)
        self.answer = (pattern, channel, data)
        self.deferred.callback(self.answer)

    def wait(self):
        return self.deferred

    def listen(self):
        self.deferred.addCallback(self._internal_callback)
        return self.client.subscribe_pattern_with_callback(self.pattern, self.pattern_callback)

    def stop(self):
        # Unregister all callback for redis messages
        return self.client.unsubscribe_pattern_with_callback(self.pattern, self.pattern_callback)

    def call(self, module_name: str, function_name: str, *args):
        import redis
        from messages.python.RPCMessage_pb2 import RPCMessage, Value
        from datetime import datetime
        import json

        print('calling', module_name, function_name, args)
        config = self.client.getConfig()
        # Get redis instance
        redis = redis.StrictRedis(host=config['hostname'], port=config['port'], db=config['db'])
        p = redis.pubsub()

        message = RPCMessage()
        message.method = function_name
        message.timestamp = datetime.now().timestamp()
        message.id = 1
        message.reply_to = self.pattern

        topic = 'module.' + module_name + '.rpc'

        #TODO args

        # Will answer on the replay_to field
        p.subscribe(message.reply_to)
        # Publish request

        redis.publish(topic, message.SerializeToString())
        # Read answer (waiting)
        # First message is for subscribe result
        message = p.get_message(timeout=5)
        # Second message is data received
        message = p.get_message(timeout=5)

        if message:
            result = json.loads(message['data'])
            return result['return_value']

        return None


