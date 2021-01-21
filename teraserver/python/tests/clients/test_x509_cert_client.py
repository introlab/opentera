import unittest


from twisted.internet import ssl, reactor
from twisted.internet import defer
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.web.client import Agent, FileBodyProducer, ResponseFailed
from twisted.web import client
from twisted.web.http_headers import Headers
from io import BytesIO
from twisted.web.iweb import IPolicyForHTTPS
from treq.multipart import MultiPartProducer
from zope.interface import implementer
import OpenSSL.crypto

import os
import opentera.crypto.crypto_utils as crypto
from cryptography.hazmat.primitives import hashes, serialization
import base64
import json

# from opentera.db.models.TeraSession import TeraSession, TeraSessionParticipants, TeraSessionStatus
import datetime


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
        defer.setDebugging(True)

        # No agent
        self.agent = None

    def tearDown(self):
        pass

    @defer.inlineCallbacks
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

        print('encoded_csr(PEM)', encoded_csr.decode('utf-8'))

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
            finished = defer.Deferred()
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
            b'https://localhost:40075/api/device/device_register',
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Content-Type': ['application/octet-stream'],
                     'Content-Transfer-Encoding': ['Base64']}),
            body)
        d.addCallbacks(gotResponse, noResponse)
        yield d
        print('_handle_device_registration')
        return certificate

    @defer.inlineCallbacks
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
            finished = defer.Deferred()
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
            b'https://localhost:40075/api/device/login',
            Headers({'User-Agent': ['Twisted Web Client Example']}),
            None)

        d.addCallbacks(gotResponse, noResponse)
        val = yield d

        print('after _handle_device_login')
        return val

    @defer.inlineCallbacks
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
            finished = defer.Deferred()
            response.deliverBody(SessionResponseReader(finished))
            return finished

        def noResponse(failure):
            failure.trap(ResponseFailed)
            print(failure.value.reasons[0].getTraceback())
            reactor.stop()

        # agent = Agent(reactor, x509ClientTest.WithCertificatePolicy())
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(login_info['device_info'])
        self.assertIsNotNone(login_info['participants_info'])
        self.assertIsNotNone(login_info['session_types_info'])

        participants_uuids = []
        for participant in login_info['participants_info']:
            participants_uuids.append(participant['participant_uuid'])

        # For now, uses the first session type in the provided list
        session_type = login_info['session_types_info'][0]
        session = {'id_session': 0,
                   # 'id_session_type': login_info['device_info']['id_session_type'],
                   'id_session_type': session_type['id_session_type'],
                   'session_name': 'File transfer test',
                   'session_start_datetime': str(datetime.datetime.now()),
                   'session_status': 0,
                   'session_participants': participants_uuids
                   }
        my_session = {'session': session}

        json_val = json.dumps(my_session)
        body = FileBodyProducer(BytesIO(json_val.encode('utf-8')))

        d = self.agent.request(
            b'POST',
            b'https://localhost:40075/api/device/sessions',
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Content-Type': ['application/json']}),
            body)

        d.addCallbacks(gotResponse, noResponse)
        val = yield d

        print('after _handle_device_session_create')
        return val

    @defer.inlineCallbacks
    def _handle_device_upload_file(self, session_info):
        class UploadResponseReader(Protocol):
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

        # /api/device/device_upload
        def gotResponse(response):
            # Reading response
            finished = defer.Deferred()
            response.deliverBody(UploadResponseReader(finished))
            return finished

        def noResponse(failure):
            failure.trap(ResponseFailed)
            print(failure.value.reasons[0].getTraceback())
            reactor.stop()

        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(session_info)

        # 100 Mb of data
        producer = MultiPartProducer(
            {
                "id_session": str(session_info['id_session']),
                # Fields, Boundary, Coordinator. When Boundary==None, generate a boundary
                "file": ('OpenIMU.dat', None, FileBodyProducer(BytesIO(os.urandom(1024 * 1024))))
            })

        d = self.agent.request(
            b'POST',
            b'https://localhost:40075/api/device/device_upload',
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Content-Type': ['multipart/form-data; boundary={}'.format(producer.boundary.decode('utf-8'))]
                     }),
            bodyProducer=producer)

        d.addCallbacks(gotResponse, noResponse)
        val = yield d

        print('after _handle_device_session_create')
        return val

    # STEP 1 : REGISTER DEVICE AND GET A CERTIFICATE
    def test_https_device_registration(self):
        self._handle_device_registration()
        reactor.run()

    # STEP 2 : Verify if certificate and key files exist
    def test_certificate_files(self):
        # Verify if certificate file exist
        basepath = os.getcwd()
        self.assertTrue(os.path.exists(x509ClientTest.CERT_FILE))
        self.assertTrue(os.path.exists(x509ClientTest.KEY_FILE))

    # STEP 3 : Test Login device
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

    # STEP 4 : Login and create session ...
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

    # STEP 5 : Upload a file
    # Device must be manually enabled first...
    def test_https_device_upload(self):

        def upload_callback(result, myself: x509ClientTest):
            print('upload_callback', result, myself)

            # Job done!
            reactor.stop()

        def session_callback(result,  myself: x509ClientTest):
            print('session_callback', result, myself)

            myself.assertIsNotNone(result)

            d = myself._handle_device_upload_file(result)
            d.addCallback(upload_callback, myself)

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

        # First step, login
        d = self._handle_device_login()
        d.addCallback(login_callback, self)
        reactor.run()
