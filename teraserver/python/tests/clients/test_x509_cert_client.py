import unittest

from OpenSSL import SSL
from twisted.internet import ssl, reactor
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.web.client import Agent, FileBodyProducer, ResponseFailed
from twisted.web import client
from twisted.web.http_headers import Headers
from io import BytesIO
from twisted.web.iweb import IPolicyForHTTPS
from zope.interface import implementer
import OpenSSL.crypto

import os


@implementer(IPolicyForHTTPS)
class MyPolicy(client.BrowserLikePolicyForHTTPS):
    def creatorForNetloc(self, hostname, port):

        # val = super().creatorForNetloc(hostname, port)

        # Read certificate
        f = open('../../certificates/devices/client_certificate.pem')
        cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())
        f.close()

        # Read private key
        f = open('../../certificates/devices/client_key.pem')
        key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read())
        f.close()

        # Do not verify certificates
        options = ssl.CertificateOptions(privateKey=key,
                                         certificate=cert,
                                         verify=False)

        return options


class x509ClientTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_certificate_files(self):
        # Verify if certificate file exist
        basepath = os.getcwd()
        self.assertTrue(os.path.exists('../../certificates/devices/client_certificate.pem'))
        self.assertTrue(os.path.exists('../../certificates/devices/client_key.pem'))

    def test_https_device_certificate(self):

        def gotResponse(response):
            print(response.code)
            reactor.stop()

        def noResponse(failure):
            failure.trap(ResponseFailed)
            print(failure.value.reasons[0].getTraceback())
            reactor.stop()

        # Agent with SSL Policy
        agent = Agent(reactor, MyPolicy())

        # body = FileBodyProducer(BytesIO(b"hello, world"))
        d = agent.request(
            b'GET',
            b'https://localhost:4040/api/device_upload',
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Content-Type': ['text/x-greeting']}),
            None)

        d.addCallbacks(gotResponse, noResponse)

        reactor.run()

