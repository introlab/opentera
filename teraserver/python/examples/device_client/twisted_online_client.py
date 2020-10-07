from twisted.internet import ssl, reactor
from twisted.web.client import Agent, readBody
from twisted.web import client
from twisted.web.http_headers import Headers
from twisted.internet import defer
from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred
from twisted.web.iweb import IPolicyForHTTPS
from treq.multipart import MultiPartProducer
from zope.interface import implementer
import OpenSSL.crypto
import json
import sys
from twisted.python import log
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import clientFromString
from autobahn.twisted.websocket import create_client_agent, WebSocketClientProtocol, WebSocketClientFactory, connectWS
from twisted.internet.ssl import ClientContextFactory


class TeraDeviceWebsocketProtocol(WebSocketClientProtocol):

    # def onOpen(self):
    #     print('onOpen')

    def onConnect(self, response):
        print('onConnect', response)

    def connectionMade(self):
        print('connectionMade')
        super().connectionMade()

    def connectionLost(self, reason):
        print('connectionLost', reason)
        super().connectionLost(reason)

    def dataReceived(self, data):
        print('dataReceived:', data)


def verify_callback(connection, x509, errnum, errdepth, ok):
    print('verify_callback')

    if not ok:
        print('Invalid cert from subject:', connection, x509.get_subject(), errnum, errdepth, ok)
        return True
    else:
        print("Certs are fine", connection, x509.get_subject(), errnum, errdepth, ok)

    return True


class TeraDeviceClientContextFactory(ClientContextFactory):
    def __init__(self, key, cert, ca):
        self.key = key
        self.cert = cert
        self.ca = ca

    def getContext(self):
        ctx = self._contextFactory(self.method)
        # See comment in DefaultOpenSSLContextFactory about SSLv2.
        ctx.use_certificate(self.cert)
        ctx.use_privatekey(self.key)
        ctx.add_client_ca(self.ca)
        ctx.add_extra_chain_cert(self.ca)
        # options = ssl.CertificateOptions(privateKey=self.key, certificate=self.cert, verify=False)
        ctx.set_verify(OpenSSL.SSL.VERIFY_NONE, verify_callback)
        ctx.set_options(OpenSSL.SSL.OP_NO_SSLv2)
        return ctx


@implementer(IPolicyForHTTPS)
class WithCertificatePolicy(client.BrowserLikePolicyForHTTPS):
    def creatorForNetloc(self, hostname, port):
        # Read certificate
        f = open('certificate.pem')
        cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())
        f.close()

        # Read private key
        f = open('private_key.pem')
        key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read())
        f.close()

        # Do not verify certificates
        options = ssl.CertificateOptions(privateKey=key,
                                         certificate=cert,
                                         verify=False)
        return options


# Agent will use certificate policy
agent = Agent(reactor, WithCertificatePolicy())

websocket_agent = None


@defer.inlineCallbacks
def login_callback(response):
    print('login_callback', response)
    if response.code == 200:
        print('Login success')
        body = yield readBody(response)
        result = json.loads(body)
        print(result)
        if 'websocket_url' in result:
            websocket_url = result['websocket_url']
            print('Should connect to websocket URL : ', websocket_url)
            # factory = Factory.forProtocol(TeraDeviceWebsocketClient)

            # factory = WebSocketClientFactory(websocket_url)
            factory = WebSocketClientFactory(websocket_url)
            factory.protocol = TeraDeviceWebsocketProtocol

            # Read CA certificate from file
            with open('ca_certificate.pem') as f:
                # trust_root = ssl.Certificate.loadPEM(f.read())
                trust_root = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())
            # Read device cert & key from file
            with open('private_key.pem') as f:
                key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read())
            with open('certificate.pem') as f:
                cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())

            # We need to attach the client and server certificates to our websocket
            # factory so it can successfully connect to the remote API.

            context = TeraDeviceClientContextFactory(key, cert, trust_root)
            connectWS(factory, context)
    else:
        print('Error login', response.code, response.phrase)

if __name__ == '__main__':
    # Logging to stdout
    log.startLogging(sys.stdout)

    print('Twisted Client Starting...')

    defer.setDebugging(True)

    # Request will generate a defered
    d = agent.request(
        b'GET',
        b'https://localhost:40075/api/device/login',
        Headers({'User-Agent': ['Twisted Device Client Example']}),
        None
    )
    d.addCallback(login_callback)

    # Infinite event loop
    reactor.run()
