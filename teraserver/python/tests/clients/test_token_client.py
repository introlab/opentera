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

# from libtera.db.models.TeraSession import TeraSession, TeraSessionParticipants, TeraSessionStatus
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

    # STEP 1 : REGISTER DEVICE AND GET A CERTIFICATE
    def test_https_device_registration(self):
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
    def test_https_device_login(self):
        token = self.getToken()
        print(token)
