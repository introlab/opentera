# Event based, twisted redis
import txredisapi as txredis


class redisProtocol(txredis.SubscriberProtocol):
    def __init__(self, charset="utf-8", errors="strict", parent=None):
        print('redisProtocol init with args', charset, errors, parent)
        super().__init__(charset, errors)
        self.parent = parent
        if self.parent:
            self.parent.setProtocol(self)

    def connectionMade(self):
        # print('redisProtocol connectionMade')
        if self.parent:
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


class RedisProtocolFactory(txredis.SubscriberFactory):

    maxDelay = 120
    continueTrying = True
    protocol = None

    def __init__(self, parent, protocol):
        super().__init__()
        print('setting arg', parent)
        print('setting protocol', protocol)
        self.parent = parent
        self.protocol = protocol

    def buildProtocol(self, addr):
        """
        This overloaded function is called when a new protocol (effective connection to the redis server) is
        performed.
        :param addr:
        :return:
        """
        print('build Protocol addr:', addr)
        if hasattr(self, 'charset'):
            p = self.protocol(self.charset, parent=self.parent)
        else:
            p = self.protocol(parent=self.parent)
        p.factory = self
        p.timeOut = self.replyTimeout
        return p
