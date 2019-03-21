from .RedisClient import RedisClient
import threading


class AsyncRedisSubscribeWait:

    def __init__(self, pattern, client: RedisClient):
        self.event = threading.Event()
        self.pattern = pattern
        self.client = client
        self.answer = (None, None, None)

    def pattern_callback(self, pattern, channel, data):
        print(self, 'pattern_callback', pattern, channel, data)
        self.event.set()
        self.answer = (pattern, channel, data)

    def wait(self, timeout=None):
        self.event.wait(timeout)
        return self.answer

    def listen(self):
        # Register all callback for redis messages
        self.client.subscribe_pattern_with_callback(self.pattern, self.pattern_callback)

    def stop(self):
        # Unregister all callback for redis messages
        self.client.unsubscribe_pattern_with_callback(self.pattern, self.pattern_callback)
