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
import json
import os

# from opentera.db.models.TeraSession import TeraSession, TeraSessionParticipants, TeraSessionStatus
import datetime


class TokenClientTest(unittest.TestCase):
    TOKEN_FILE = os.getcwd() + '/device.token.json'

    @implementer(IPolicyForHTTPS)
    class NoCertificatePolicy(client.BrowserLikePolicyForHTTPS):
        def creatorForNetloc(self, hostname, port):
            # Do not verify certificates
            options = ssl.CertificateOptions(verify=False)

            return options

    def setUp(self):
        # Defer set debugging
        defer.setDebugging(True)

        # No agent
        self.agent = None

    def tearDown(self):
        pass

    @staticmethod
    def getToken():
        with open(TokenClientTest.TOKEN_FILE, 'r') as f:
            data = json.load(f)
            # TokenClientTest.assertEquals(True, data.__contains__('token'))
            return data['token']

    @defer.inlineCallbacks
    def _handle_device_registration(self):

        registration_info = None

        class RegistrationReader(Protocol):
            def __init__(self, finished):
                self.finished = finished

            def dataReceived(self, bytes):
                # We should have our new certificate, json format
                result = json.loads(bytes.decode('utf-8'))

                with open(TokenClientTest.TOKEN_FILE, 'w') as f:
                    json.dump(result, f)

                global registration_info
                registration_info = result
                print(registration_info)

            def connectionLost(self, reason):
                # print('Finished receiving body:', reason)
                self.finished.callback(None)
                reactor.stop()

        def gotResponse(response):
            print(response.code)
            # Reading response
            finished = defer.Deferred()
            response.deliverBody(RegistrationReader(finished))
            return finished

        def noResponse(failure):
            failure.trap(ResponseFailed)
            print(failure.value.reasons[0].getTraceback())
            reactor.stop()

        # Agent with NO SSL policy
        agent = Agent(reactor, TokenClientTest.NoCertificatePolicy())

        request = {'device_info': {'device_name': 'Test Device'}}

        json_data = json.dumps(request)

        # JSON Body...
        body = FileBodyProducer(BytesIO(json_data.encode('utf-8')))

        # A Simple get method
        d = agent.request(
            b'POST',
            b'https://localhost:4040/api/device/device_register',
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Content-Type': ['application/json']}),
            body)
        d.addCallbacks(gotResponse, noResponse)
        yield d
        print('_handle_device_registration', registration_info)
        return registration_info

    @defer.inlineCallbacks
    def _handle_device_login_with_bearer_token(self, token=None):

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
        self.assertIsNotNone(token)

        d = self.agent.request(
            b'GET',
            b'https://localhost:4040/api/device/device_login',
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Authorization': ['OpenTera ' + token]}),
            None)

        d.addCallbacks(gotResponse, noResponse)
        val = yield d

        print('after _handle_device_login')
        return val

    @defer.inlineCallbacks
    def _handle_device_login(self, token=None):

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
        self.assertIsNotNone(token)

        d = self.agent.request(
            b'GET',
            b'https://localhost:4040/api/device/device_login' + b'?token=' + token.encode('utf-8'),
            Headers({'User-Agent': ['Twisted Web Client Example']}),
            None)

        d.addCallbacks(gotResponse, noResponse)
        val = yield d

        print('after _handle_device_login')
        return val

    @defer.inlineCallbacks
    def _handle_device_session_create(self, login_info, token):

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
            b'https://localhost:4040/api/device/sessions' + b'?token=' + token.encode('utf-8'),
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Content-Type': ['application/json']}),
            body)

        d.addCallbacks(gotResponse, noResponse)
        val = yield d

        print('after _handle_device_session_create')
        return val

    @defer.inlineCallbacks
    def _handle_device_upload_file(self, session_info, token):
        class UploadResponseReader(Protocol):
            def __init__(self, finished):
                self.finished = finished

            def dataReceived(self, data):
                # We should have our new certificate, json format
                result = json.loads(data.decode('utf-8'))
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
        self.assertIsNotNone(token)

        # 1 Mb of data
        producer = MultiPartProducer(
            {
                "id_session": str(session_info['id_session']),
                # Fields, Boundary, Coordinator. When Boundary==None, generate a boundary
                "file": ('OpenIMU.dat', None, FileBodyProducer(BytesIO(os.urandom(1024 * 1024))))
            })

        d = self.agent.request(
            b'POST',
            b'https://localhost:4040/api/device/device_upload' + b'?token=' + token.encode('utf-8'),
            Headers({'User-Agent': ['Twisted Web Client Example'],
                     'Content-Type': ['multipart/form-data; boundary={}'.format(producer.boundary.decode('utf-8'))]
                     }),
            bodyProducer=producer)

        d.addCallbacks(gotResponse, noResponse)
        val = yield d

        print('after _handle_device_session_create')
        return val

    # STEP 1 : REGISTER DEVICE AND GET A CERTIFICATE
    def test_http_device_registration(self):
        self._handle_device_registration()
        reactor.run()

    # STEP 2 : VERIFY TOKEN FILE
    def test_token_file_valid(self):
        self.assertTrue(os.path.exists(TokenClientTest.TOKEN_FILE))
        try:
            token = TokenClientTest.getToken()
            self.assertNotEqual(0, len(token))
        except:
            self.assertTrue(False)

    # STEP 3 : LOGIN WITH TOKEN
    def test_http_device_login(self):
        token = self.getToken()
        print(token)

        def login_callback(result, myself: TokenClientTest):
            print('login_callback', result, myself)

            # Test result
            myself.assertIsNotNone(result)

            # Job done!
            reactor.stop()

        # Create the ssl agent
        self.agent = Agent(reactor, TokenClientTest.NoCertificatePolicy())

        d = self._handle_device_login(token)
        d.addCallback(login_callback, self)
        reactor.run()

    # STEP 3.1: LOGIN WITH BEARER TOKEN
    def test_http_device_login_with_bearer_token(self):
        token = self.getToken()
        print(token)

        def login_callback(result, myself: TokenClientTest):
            print('login_callback', result, myself)

            # Test result
            myself.assertIsNotNone(result)

            # Job done!
            reactor.stop()

        # Create the ssl agent
        self.agent = Agent(reactor, TokenClientTest.NoCertificatePolicy())

        d = self._handle_device_login_with_bearer_token(token)
        d.addCallback(login_callback, self)
        reactor.run()

    # STEP 4 : Login and create session ...
    def test_http_device_create_session(self):
        token = self.getToken()
        print(token)

        def session_callback(result,  myself: TokenClientTest):
            print('result', result, myself)

            # Job done
            reactor.stop()

        def login_callback(result, myself: TokenClientTest):
            print('login_callback', result, myself)

            # Test result
            myself.assertIsNotNone(result)

            d2 = myself._handle_device_session_create(result, token)
            d2.addCallback(session_callback, myself)

            # Job done!
            # reactor.stop()

        # Create agent with certificates
        self.agent = Agent(reactor, TokenClientTest.NoCertificatePolicy())

        d1 = self._handle_device_login(token)
        d1.addCallback(login_callback, self)
        reactor.run()

    # STEP 5 : Upload a file
    # Device must be manually enabled first...
    def test_http_device_upload(self):

        token = self.getToken()
        print(token)

        def upload_callback(result, myself: TokenClientTest):
            print('upload_callback', result, myself)

            # Job done!
            reactor.stop()

        def session_callback(result,  myself: TokenClientTest):
            print('session_callback', result, myself)

            myself.assertIsNotNone(result)

            d = myself._handle_device_upload_file(result, token)
            d.addCallback(upload_callback, myself)

        def login_callback(result, myself: TokenClientTest):
            print('login_callback', result, myself)

            # Test result
            myself.assertIsNotNone(result)

            d = myself._handle_device_session_create(result, token)
            d.addCallback(session_callback, myself)

            # Job done!
            # reactor.stop()

        # Create agent with certificates
        self.agent = Agent(reactor, TokenClientTest.NoCertificatePolicy())

        # First step, login
        d = self._handle_device_login(token)
        d.addCallback(login_callback, self)
        reactor.run()
