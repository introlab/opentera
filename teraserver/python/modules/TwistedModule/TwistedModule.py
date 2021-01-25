from modules.FlaskModule.FlaskModule import flask_app
from opentera.modules.BaseModule import BaseModule, ModuleNames
from opentera.config.ConfigManager import ConfigManager


# Same directory
from .TwistedModuleWebSocketServerFactory import TwistedModuleWebSocketServerFactory
from .TeraWebSocketServerUserProtocol import TeraWebSocketServerUserProtocol
from .TeraWebSocketServerParticipantProtocol import TeraWebSocketServerParticipantProtocol
from .TeraWebSocketServerDeviceProtocol import TeraWebSocketServerDeviceProtocol

# WebSockets
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource

# Twisted
from twisted.internet import reactor, ssl
from twisted.web.http import HTTPChannel
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web import resource
from twisted.web.wsgi import WSGIResource
from twisted.python import log
from OpenSSL import SSL
import sys
import os


class MyHTTPChannel(HTTPChannel):
    def allHeadersReceived(self):
        # Verify if we have a client with a certificate...
        # cert = self.transport.getPeerCertificate()
        cert = None
        if getattr(self.transport, "getPeerCertificate", None):
            cert = self.transport.getPeerCertificate()

        # Current request
        req = self.requests[-1]

        # SAFETY X-Device-UUID, X-Participant-UUID must not be set in header before testing certificate
        if req.requestHeaders.hasHeader('X-Device-UUID'):
            req.requestHeaders.removeHeader('X-Device-UUID')
            # TODO raise error?

        if req.requestHeaders.hasHeader('X-Participant-UUID'):
            req.requestHeaders.removeHeader('X-Participant-UUID')
            # TODO raise error ?
        #
        # if cert is not None:
        #     # Certificate found, add information in header
        #     subject = cert.get_subject()
        #     # Get UID if possible
        #     if 'Device' in subject.CN and hasattr(subject, 'UID'):
        #         user_id = subject.UID
        #         req.requestHeaders.addRawHeader('X-Device-UUID', user_id)
        #     if 'Participant' in subject.CN and hasattr(subject, 'UID'):
        #         user_id = subject.UID
        #         req.requestHeaders.addRawHeader('X-Participant-UUID', user_id)

        # Look for nginx headers (can contain a certificate)
        if req.requestHeaders.hasHeader('x-ssl-client-dn'):
            # TODO do better parsing. Working for now...
            # Domain extracted by nginx (much faster)
            client_dn = req.requestHeaders.getRawHeaders('x-ssl-client-dn')[0]
            uuid = ''
            for key in client_dn.split(','):
                if 'UID' in key and len(key) == 40:
                    uuid = key[4:]
                if 'CN' in key and 'Device' in key:
                    req.requestHeaders.addRawHeader('X-Device-UUID', uuid)
                if 'CN' in key and 'Participant' in key:
                    req.requestHeaders.addRawHeader('X-Participant-UUID', uuid)

        HTTPChannel.allHeadersReceived(self)


class MySite(Site):
    protocol = MyHTTPChannel

    def __init__(self, resource, requestFactory=None, *args, **kwargs):
        super().__init__(resource, requestFactory, *args, **kwargs)


class TwistedModule(BaseModule):

    def __init__(self, config: ConfigManager):

        BaseModule.__init__(self, ModuleNames.TWISTED_MODULE_NAME.value, config)

        # create a Twisted Web resource for our WebSocket server
        # Use IP stored in config

        # USERS
        wss_user_factory = TwistedModuleWebSocketServerFactory(u"wss://%s:%d" % (self.config.server_config['hostname'],
                                                                                 self.config.server_config['port']),
                                                               redis_config=self.config.redis_config)

        wss_user_factory.protocol = TeraWebSocketServerUserProtocol
        wss_user_resource = WebSocketResource(wss_user_factory)

        # PARTICIPANTS
        wss_participant_factory = TwistedModuleWebSocketServerFactory(u"wss://%s:%d" %
                                                                      (self.config.server_config['hostname'],
                                                                       self.config.server_config['port']),
                                                                      redis_config=self.config.redis_config)

        wss_participant_factory.protocol = TeraWebSocketServerParticipantProtocol
        wss_participant_resource = WebSocketResource(wss_participant_factory)

        # DEVICES
        wss_device_factory = TwistedModuleWebSocketServerFactory(u"wss://%s:%d" %
                                                                 (self.config.server_config['hostname'],
                                                                  self.config.server_config['port']),
                                                                 redis_config=self.config.redis_config)

        wss_device_factory.protocol = TeraWebSocketServerDeviceProtocol
        wss_device_resource = WebSocketResource(wss_device_factory)

        # create a Twisted Web WSGI resource for our Flask server
        wsgi_resource = WSGIResource(reactor, reactor.getThreadPool(), flask_app)

        # create resource for static assets
        # static_resource = File(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'assets'))
        base_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        static_resource = File(os.path.join(base_folder, 'static'))
        static_resource.contentTypes['.js'] = 'text/javascript'
        static_resource.forbidden = True

        # the path "/assets" served by our File stuff and
        # the path "/wss" served by our WebSocket stuff
        # root_resource = WSGIRootResource(wsgi_resource, {b'wss': wss_resource})

        # Avoid using the wss resource at root level
        wss_root = resource.ForbiddenResource()

        wss_root.putChild(b'user', wss_user_resource)
        wss_root.putChild(b'participant', wss_participant_resource)
        wss_root.putChild(b'device', wss_device_resource)

        # Establish root resource
        root_resource = WSGIRootResource(wsgi_resource, {b'assets': static_resource, b'wss': wss_root})

        # Create a Twisted Web Site
        site = MySite(root_resource)

        # List of available CA clients certificates
        # TODO READ OTHER CERTIFICATES FROM FILE/DB...
        # caCerts=[cert.original]
        caCerts = []

        # Use verify = True to verify certificates
        self.ssl_factory = ssl.CertificateOptions(verify=False, caCerts=caCerts,
                                                  requireCertificate=False,
                                                  enableSessions=False)

        ctx = self.ssl_factory.getContext()
        ctx.use_privatekey_file(self.config.server_config['ssl_path'] + '/'
                                + self.config.server_config['site_private_key'])

        ctx.use_certificate_file(self.config.server_config['ssl_path'] + '/'
                                 + self.config.server_config['site_certificate'])

        # Certificate verification callback
        ctx.set_verify(SSL.VERIFY_NONE, self.verifyCallback)

        # With self-signed certs we have to explicitely tell the server to trust certificates
        ctx.load_verify_locations(self.config.server_config['ssl_path'] + '/'
                                  + self.config.server_config['ca_certificate'])

        if self.config.server_config['use_ssl']:
            reactor.listenSSL(self.config.server_config['port'], site, self.ssl_factory)
        else:
            reactor.listenTCP(self.config.server_config['port'], site)

    def __del__(self):
        pass

    def verifyCallback(self, connection, x509, errnum, errdepth, ok):
        # 'b707e0b2-e649-47e7-a938-2b949c423f73'
        # errnum 24=invalid CA certificate...

        if not ok:
            print('Invalid cert from subject:', connection, x509.get_subject(), errnum, errdepth, ok)
            return False
        else:
            print("Certs are fine", connection, x509.get_subject(), errnum, errdepth, ok)

        return True

    def setup_module_pubsub(self):
        # Additional subscribe
        pass

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('TwistedModule - Received message ', pattern, channel, message)
        pass

    def run(self):
        log.startLogging(sys.stdout)
        reactor.run()



