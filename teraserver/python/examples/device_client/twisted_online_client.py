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

    def connectionLost(self, reason):
        print('connectionLost', reason)

    def dataReceived(self, data):
        print('dataReceived:', data)


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

            factory = WebSocketClientFactory(websocket_url)
            factory.protocol = TeraDeviceWebsocketProtocol

            # Read CA certificate from file
            with open('ca_certificate.pem') as ca_cert:
                trust_root = ssl.Certificate.loadPEM(ca_cert.read())

            # Read device cert & key from file
            with open('private_key.pem') as f:
                key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read())
            with open('certificate.pem') as f:
                cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())

            # We need to attach the client and server certificates to our websocket
            # factory so it can successfully connect to the remote API.
            options = ssl.CertificateOptions(privateKey=key, certificate=cert)
            context = ssl.ClientContextFactory()
            connectWS(factory, context)


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
