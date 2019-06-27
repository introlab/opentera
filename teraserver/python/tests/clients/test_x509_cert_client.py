import unittest

from OpenSSL import SSL
from twisted.internet import ssl, reactor
from twisted.internet.defer import Deferred, inlineCallbacks, setDebugging
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
import json


class x509ClientTest(unittest.TestCase):
    # File information
    KEY_FILE = os.getcwd() + '/device.key.pem'
    CERT_FILE = os.getcwd() + '/device.cert.pem'

    @implementer(IPolicyForHTTPS)
    class NoCertificatePolicy(client.BrowserLikePolicyForHTTPS):
        def creatorForNetloc(self, hostname, port):
            # Do not verify certificates
            options = ssl.CertificateOptions(verify=False)

            return options

    @implementer(IPolicyForHTTPS)
    class WithCertificatePolicy(client.BrowserLikePolicyForHTTPS):
        def creatorForNetloc(self, hostname, port):
            # val = super().creatorForNetloc(hostname, port)

            # Read certificate
            f = open(x509ClientTest.CERT_FILE)
            cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())
            f.close()

            # Read private key
            f = open(x509ClientTest.KEY_FILE)
            key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read())
            f.close()

            # Do not verify certificates
            options = ssl.CertificateOptions(privateKey=key,
                                             certificate=cert,
                                             verify=False)

            return options

    def setUp(self):
        # Defer set debugging
        setDebugging(True)

        # No agent
        self.agent = None

    def tearDown(self):
        pass

    @inlineCallbacks
    def _handle_device_registration(self):

        certificate = None

        # This will generate private key and signing request for the CA
        client_info = crypto.create_certificate_signing_request('Test AppleWatch to be registered')

        # Write private key
        with open(x509ClientTest.KEY_FILE, 'wb') as f:
            f.write(client_info['private_key'].private_bytes(serialization.Encoding.PEM,
                                                             serialization.PrivateFormat.TraditionalOpenSSL,
                                                             serialization.NoEncryption()))

        # Encode in PEM format
        encoded_csr = client_info['csr'].public_bytes(serialization.Encoding.PEM)

        class CertificateReader(Protocol):
            def __init__(self, finished):
                self.finished = finished

            def dataReceived(self, bytes):
                # We should have our new certificate, json format
                result = json.loads(bytes.decode('utf-8'))

                # Write the certificate
                with open(x509ClientTest.CERT_FILE, 'wb') as f:
                    f.write(result['certificate'].encode('utf-8'))

                global certificate
                certificate = result
                print(result)

            def connectionLost(self, reason):
                # print('Finished receiving body:', reason)
                self.finished.callback(None)
                reactor.stop()

        def gotResponse(response):
            print(response.code)
            # Reading response
            finished = Deferred()
            response.deliverBody(CertificateReader(finished))
            return finished

        def noResponse(failure):
            failure.trap(ResponseFailed)
            print(failure.value.reasons[0].getTraceback())
            reactor.stop()

        # Agent with NO SSL policy
        agent = Agent(reactor, x509ClientTest.NoCertificatePolicy())

        body = FileBodyProducer(BytesIO(encoded_csr))

        d = agent.request(
            b'POST',
            b'https://localhost:4040/api/device/device_register',
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Content-Type': ['application/octet-stream'],
                     'Content-Transfer-Encoding': ['Base64']}),
            body)
        d.addCallbacks(gotResponse, noResponse)
        yield d
        print('_handle_device_registration')
        return certificate

    @inlineCallbacks
    def _handle_device_login(self):

        class LoginResponseReader(Protocol):
            def __init__(self, finished):
                self.finished = finished

            def dataReceived(self, bytes):
                # We should have our new certificate, json format
                result = json.loads(bytes.decode('utf-8'))
                print('dataReceived', result)
                # Call deferred callback...
                self.finished.callback(result)

            def connectionLost(self, reason):
                # print('Finished receiving body:', reason)
                # reactor.stop()
                # self.finished.callback(None)
                pass

        def gotResponse(response):
            # Reading response
            finished = Deferred()
            response.deliverBody(LoginResponseReader(finished))
            return finished

        def noResponse(failure):
            failure.trap(ResponseFailed)
            print(failure.value.reasons[0].getTraceback())
            reactor.stop()

        # agent = Agent(reactor, x509ClientTest.WithCertificatePolicy())
        self.assertIsNotNone(self.agent)

        d = self.agent.request(
            b'GET',
            b'https://localhost:4040/api/device/device_login',
            Headers({'User-Agent': ['Twisted Web Client Example']}),
            None)

        d.addCallbacks(gotResponse, noResponse)
        val = yield d

        print('after _handle_device_login')
        return val

    @inlineCallbacks
    def _handle_device_session_create(self, login_info):

        class SessionResponseReader(Protocol):
            def __init__(self, finished):
                self.finished = finished

            def dataReceived(self, bytes):
                # We should have our new certificate, json format
                result = json.loads(bytes.decode('utf-8'))
                print('dataReceived', result)
                # Call defered callback...
                self.finished.callback(result)

            def connectionLost(self, reason):
                # print('Finished receiving body:', reason)
                # reactor.stop()
                # self.finished.callback(None)
                pass

        # /api/device/sessions
        def gotResponse(response):
            # Reading response
            finished = Deferred()
            response.deliverBody(SessionResponseReader(finished))
            return finished

        def noResponse(failure):
            failure.trap(ResponseFailed)
            print(failure.value.reasons[0].getTraceback())
            reactor.stop()

        # agent = Agent(reactor, x509ClientTest.WithCertificatePolicy())
        self.assertIsNotNone(self.agent)

        d = self.agent.request(
            b'GET',
            b'https://localhost:4040/api/device/sessions',
            Headers({'User-Agent': ['Twisted Web Client Example']}),
            None)

        d.addCallbacks(gotResponse, noResponse)
        val = yield d

        print('after _handle_device_session_create')
        return val

    # STEP 1 : REGISTER DEVICE AND GET A CERTIFICATE
    def test_https_device_registration(self):
        self._handle_device_registration()
        reactor.run()

    # STEP 2, verify if certificate and key files exist
    def test_certificate_files(self):
        # Verify if certificate file exist
        basepath = os.getcwd()
        self.assertTrue(os.path.exists(x509ClientTest.CERT_FILE))
        self.assertTrue(os.path.exists(x509ClientTest.KEY_FILE))

    # STEP 3. Test Login device
    def test_https_device_login(self):

        def login_callback(result, myself: x509ClientTest):
            print('login_callback', result, myself)

            # Test result
            myself.assertIsNotNone(result)

            # Job done!
            reactor.stop()

        # Create agent with certificates
        self.agent = Agent(reactor, x509ClientTest.WithCertificatePolicy())

        d = self._handle_device_login()
        d.addCallback(login_callback, self)
        reactor.run()

    # STEP 4: Login and create session ...
    def test_https_device_create_session(self):

        def session_callback(result,  myself: x509ClientTest):
            print('result', result, myself)

            # Job done
            reactor.stop()

        def login_callback(result, myself: x509ClientTest):
            print('login_callback', result, myself)

            # Test result
            myself.assertIsNotNone(result)

            d = myself._handle_device_session_create(result)
            d.addCallback(session_callback, myself)

            # Job done!
            # reactor.stop()

        # Create agent with certificates
        self.agent = Agent(reactor, x509ClientTest.WithCertificatePolicy())

        d = self._handle_device_login()
        d.addCallback(login_callback, self)
        reactor.run()

    # STEP 3: connect to server to upload a file...
    # Device must be manually enabled first...
    def test_https_device_certificate(self):

        def gotResponse(response):
            print('gotResponse, SSL OK')
            print(response.code)
            print(response)
            reactor.stop()

        def noResponse(failure):
            print('noResponse, SSL Failed')
            failure.trap(ResponseFailed)
            print(failure.value.reasons[0].getTraceback())
            reactor.stop()

        # Agent with SSL Policy
        agent = Agent(reactor, x509ClientTest.WithCertificatePolicy())

        # body = FileBodyProducer(BytesIO(b"hello, world"))
        d = agent.request(
            b'GET',
            b'https://localhost:4040/api/device/device_upload',
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Content-Type': ['text/x-greeting']}),
            None)

        d.addCallbacks(gotResponse, noResponse)

        reactor.run()
