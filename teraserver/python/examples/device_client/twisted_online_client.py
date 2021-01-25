from twisted.internet import ssl, reactor
from twisted.web.client import Agent, readBody
from twisted.web import client
from twisted.web.http_headers import Headers
from twisted.internet import defer
from twisted.web.iweb import IPolicyForHTTPS
from zope.interface import implementer
import OpenSSL.crypto
import json
import sys
from twisted.python import log
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS
from twisted.internet.ssl import ClientContextFactory

import opentera.messages.python as messages
from google.protobuf.json_format import ParseDict, ParseError


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
        # This is a security issue. Needed for self signed certificates.
        options = ssl.CertificateOptions(privateKey=key,
                                         certificate=cert,
                                         verify=False)
        return options


# Agent will use certificate policy
agent = Agent(reactor, WithCertificatePolicy())


class TeraDeviceWebsocketProtocol(WebSocketClientProtocol):

    def onMessage(self, payload, isBinary):
        # TODO remove debug
        print('onMessage', payload, isBinary)
        try:
            # TODO Handle more events
            json_dict = json.loads(payload)
            if 'message' in json_dict:
                message = ParseDict(json_dict['message'], messages.TeraEvent(), ignore_unknown_fields=True)
                # TODO remove debug
                print(message)
                for any_msg in message.events:
                    # Test for DeviceEvent
                    device_event = messages.DeviceEvent()
                    if any_msg.Unpack(device_event):
                        # TODO Handle device_event
                        pass

                    # Test for JoinSessionEvent
                    join_session_event = messages.JoinSessionEvent()
                    if any_msg.Unpack(join_session_event):
                        # TODO Handle join_session_event
                        pass

                    # Test for ParticipantEvent
                    participant_event = messages.ParticipantEvent()
                    if any_msg.Unpack(participant_event):
                        # TODO Handle participant_event
                        pass

                    # Test for StopSessionEvent
                    stop_session_event = messages.StopSessionEvent()
                    if any_msg.Unpack(stop_session_event):
                        # TODO Handle stop_session_event
                        pass

                    # Test for UserEvent
                    user_event = messages.UserEvent()
                    if any_msg.Unpack(user_event):
                        # TODO Handle user_event
                        pass

                    # Test for LeaveSessionEvent
                    leave_session_event = messages.LeaveSessionEvent()
                    if any_msg.Unpack(leave_session_event):
                        # TODO Handle leave_session_event
                        pass

                    # Test for JoinSessionReply
                    join_session_reply = messages.JoinSessionReplyEvent()
                    if any_msg.Unpack(join_session_reply):
                        # TODO Handle join_session_reply
                        pass
                # Look for useful events
        except ParseError as e:
            print(e)

    def onOpen(self):
        super().onOpen()

    def onClose(self, wasClean, code, reason):
        super().onClose(wasClean, code, reason)


def verify_callback(connection, x509, errnum, errdepth, ok):
    # We always return True here, we do not verify certificates
    # This is a security issue. Needed for self signed certificates.
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
        ctx.use_certificate(self.cert)
        ctx.use_privatekey(self.key)
        ctx.add_client_ca(self.ca)
        ctx.add_extra_chain_cert(self.ca)
        ctx.set_verify(OpenSSL.SSL.VERIFY_NONE, verify_callback)
        ctx.set_options(OpenSSL.SSL.OP_NO_SSLv2)
        return ctx


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

            # Create factory that will create an instance of our protocol
            factory = WebSocketClientFactory(websocket_url)
            factory.protocol = TeraDeviceWebsocketProtocol

            # Read CA certificate, private key and certificate from file
            with open('ca_certificate.pem') as f:
                ca_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())
            with open('private_key.pem') as f:
                key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read())
            with open('certificate.pem') as f:
                cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())

            # We need to attach the client and server certificates to our websocket
            # factory so it can successfully connect to the remote API.
            context = TeraDeviceClientContextFactory(key, cert, ca_cert)
            connectWS(factory, context)
    else:
        print('Error login', response.code, response.phrase)


if __name__ == '__main__':
    # Logging to stdout
    log.startLogging(sys.stdout)

    print('Twisted Client Starting...')

    defer.setDebugging(True)

    # Request will generate a defered
    # Login is the first step
    d = agent.request(
        b'GET',
        b'https://localhost:40075/api/device/login',
        Headers({'User-Agent': ['Twisted Device Client Example']}),
        None
    )
    d.addCallback(login_callback)

    # Start event loop
    reactor.run()
