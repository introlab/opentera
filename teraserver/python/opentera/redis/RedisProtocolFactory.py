# Event based, twisted redis
import txredisapi as txredis
from twisted.internet import defer


class redisProtocol(txredis.SubscriberProtocol):
    def __init__(self, charset=None, errors="strict", parent=None, *args, **kwargs):
        # print('redisProtocol init with args', charset, errors, parent, args, kwargs)
        super().__init__(charset, errors, *args, **kwargs)
        self.parent = parent
        if self.parent:
            self.parent.setProtocol(self)

    # def __del__(self):
    #     print("****- Deleting redisProtocol")

    @defer.inlineCallbacks
    def connectionMade(self):
        # print('redisProtocol connectionMade')
        if self.parent:
            ret = yield self.execute_command('client', 'setname', 'txredis_' + self.parent.__class__.__name__)
            self.parent.redisConnectionMade()
        else:
            print('redisProtocol connectionMade')

    def messageReceived(self, pattern, channel, message):
        # print('redisProtocol message received', pattern, channel, message)
        if self.parent:
            self.parent.redisMessageReceived(pattern, channel, message)
        else:
            print('redisProtocol message received', pattern, channel, message)

    def connectionLost(self, reason):
        # print("redisProtocol lost connection", reason)
        if self.parent:
            self.parent.redisConnectionLost(reason)
        else:
            print("redisProtocol lost connection", reason)

    def replyReceived(self, reply):
        super().replyReceived(reply)


class RedisProtocolFactory(txredis.SubscriberFactory):

    maxDelay = 120
    continueTrying = True
    protocol = None

    def __init__(self, parent, protocol, config):
        super().__init__()
        # print('setting arg', parent)
        # print('setting protocol', protocol)
        self.parent = parent
        self.protocol = protocol
        self.redis_config = config

    # def __del__(self):
    #     print("****- Deleting RedisProtocolFactory")

    def buildProtocol(self, addr):
        """
        This overloaded function is called when a new protocol (effective connection to the redis server) is
        performed.
        :param addr:
        :return:
        """
        # print('build Protocol addr:', addr)
        if hasattr(self, 'charset'):
            # p = self.protocol(parent=self.parent)
            p = self.protocol(self.charset,
                              parent=self.parent,
                              password=self.redis_config['password'],
                              dbid=self.redis_config['db'])
        else:
            # Forcing no encoding
            p = self.protocol(parent=self.parent,
                              password=self.redis_config['password'],
                              dbid=self.redis_config['db'])
        p.factory = self
        p.timeOut = self.replyTimeout
        return p
