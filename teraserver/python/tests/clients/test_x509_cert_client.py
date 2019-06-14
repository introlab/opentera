import unittest

from OpenSSL import SSL
from twisted.internet import ssl, reactor
from twisted.internet.protocol import ClientFactory, Protocol
import os


class EchoClient(Protocol):
    def connectionMade(self):
        print("hello, world")

    def dataReceived(self, data):
        print("Server said:", data)


class EchoClientFactory(ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        reactor.stop()


class CtxFactory(ssl.ClientContextFactory):
    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file('../../certificates/devices/client_certificate.pem')
        # ctx.use_certificate_file('../../certificates/ca.pem')
        ctx.use_privatekey_file('../../certificates/devices/client_key.pem')
        # ctx.use_privatekey_file('../../certificates/key.pem')
        return ctx


class x509ClientTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_twisted_client(self):
        # Verify if certificate file exist
        basepath = os.getcwd()
        self.assertTrue(os.path.exists('../../certificates/devices/client_certificate.pem'))
        self.assertTrue(os.path.exists('../../certificates/devices/client_key.pem'))

        factory = EchoClientFactory()
        reactor.connectSSL('localhost', 4040, factory, CtxFactory())
        reactor.run()

