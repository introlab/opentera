from .RedisClient import RedisClient
import threading
from twisted.internet import defer


class AsyncRedisSubscribeWait:

    def __init__(self, pattern, client: RedisClient):
        self.event = threading.Event()
        self.pattern = pattern
        self.client = client
        self.answer = (None, None, None)
        self.callback = None

    def __del__(self):
        self.stop()

    def pattern_callback(self, pattern, channel, data):
        print(self, 'pattern_callback', pattern, channel, data)
        self.answer = (pattern, channel, data)
        if self.callback:
            self.callback(pattern, channel, data)
        self.event.clear()

    def wait(self, timeout=None):
        self.event.wait(timeout)
        return self.answer

    @defer.inlineCallbacks
    def listen(self, callback=None):
        # return self._listen_inline()
        self.callback = callback
        val = yield self.client.subscribe_pattern_with_callback(self.pattern, self.pattern_callback)
        return val

    def stop(self):
        # Unregister all callback for redis messages
        self.client.unsubscribe_pattern_with_callback(self.pattern, self.pattern_callback)
