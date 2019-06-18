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
import libtera.crypto.crypto_utils as crypto
from cryptography.hazmat.primitives import hashes, serialization
import base64

@implementer(IPolicyForHTTPS)
class WithCertificatePolicy(client.BrowserLikePolicyForHTTPS):
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


@implementer(IPolicyForHTTPS)
class NoCertificatePolicy(client.BrowserLikePolicyForHTTPS):
    def creatorForNetloc(self, hostname, port):
        # Do not verify certificates
        options = ssl.CertificateOptions(verify=False)

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
        agent = Agent(reactor, WithCertificatePolicy())

        # body = FileBodyProducer(BytesIO(b"hello, world"))
        d = agent.request(
            b'GET',
            b'https://localhost:4040/api/device_upload',
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Content-Type': ['text/x-greeting']}),
            None)

        d.addCallbacks(gotResponse, noResponse)

        reactor.run()

    def test_https_device_registration(self):

        # This will generate private key and signing request for the CA
        client_info = crypto.create_certificate_signing_request(user_uuid='rien')

        csr = client_info['csr']
        print(client_info['csr'])

        # Encode in base64
        # encoded_cert = base64.b64encode(client_info['csr'].tbs_certrequest_bytes)

        # Encode in PEM format
        encoded_csr = client_info['csr'].public_bytes(serialization.Encoding.PEM)

        def gotResponse(response):
            print(response.code)
            reactor.stop()

        def noResponse(failure):
            failure.trap(ResponseFailed)
            print(failure.value.reasons[0].getTraceback())
            reactor.stop()

        # Agent with NO SSL policy
        agent = Agent(reactor, NoCertificatePolicy())

        body = FileBodyProducer(BytesIO(encoded_csr))
        d = agent.request(
            b'POST',
            b'https://localhost:4040/api/device_register',
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Content-Type': ['application/octet-stream'],
                     'Content-Transfer-Encoding': ['Base64']}),
            body)

        d.addCallbacks(gotResponse, noResponse)

        reactor.run()

