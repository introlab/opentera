from modules.FlaskModule.FlaskModule import flask_app
from modules.BaseModule import BaseModule, ModuleNames
from libtera.ConfigManager import ConfigManager


# Same directory
from .TwistedModuleWebSocketServerFactory import TwistedModuleWebSocketServerFactory
from .TeraWebSocketServerProtocol import TeraWebSocketServerProtocol

# WebSockets
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource

# Twisted
from twisted.application import internet, service
from twisted.internet import reactor, ssl
from twisted.python.threadpool import ThreadPool
from twisted.web.http import HTTPChannel
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.python import log
from OpenSSL import SSL
import sys


class MyHTTPChannel(HTTPChannel):
    def allHeadersReceived(self):
        # Verify if we have a client with a certificate...
        cert = self.transport.getPeerCertificate()

        if cert is not None:
            # Certificate found, add information in header
            subject = cert.get_subject()
            # Get UID if possible
            if 'Device' in subject.CN and hasattr(subject, 'UID'):
                user_id = subject.UID
                req = self.requests[-1]
                req.requestHeaders.addRawHeader('X-Device-UUID', user_id)
            if 'Participant' in subject.CN and hasattr(subject, 'UID'):
                user_id = subject.UID
                req = self.requests[-1]
                req.requestHeaders.addRawHeader('X-Participant-UUID', user_id)

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
        wss_factory = TwistedModuleWebSocketServerFactory(u"wss://%s:%d" % (self.config.server_config['hostname'],
                                                          self.config.server_config['port']),
                                                          redis_config=self.config.redis_config)

        wss_factory.protocol = TeraWebSocketServerProtocol
        wss_resource = WebSocketResource(wss_factory)

        # create a Twisted Web WSGI resource for our Flask server
        wsgi_resource = WSGIResource(reactor, reactor.getThreadPool(), flask_app)

        # create resource for static assets
        # static_resource = File(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'assets'))

        # the path "/assets" served by our File stuff and
        # the path "/wss" served by our WebSocket stuff
        root_resource = WSGIRootResource(wsgi_resource, {b'wss': wss_resource})

        # Create a Twisted Web Site
        site = MySite(root_resource)

        # ssl_factory = ssl.DefaultOpenSSLContextFactory(
        #      privateKeyFileName=self.config.server_config['ssl_path'] + '/key.pem',
        #      certificateFileName=self.config.server_config['ssl_path'] + '/ca.pem')

        # List of available CA clients certificates

        # Test certificate
        cert = ssl.Certificate.loadPEM(open(self.config.server_config['ssl_path'] +
                                            '/devices/client_certificate.pem', 'rb').read())

        # TODO READ OTHER CERTIFICATES FROM DB...
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
        ctx.set_verify(SSL.VERIFY_PEER, self.verifyCallback)

        # With self-signed certs we have to explicitely tell the server to trust certificates
        ctx.load_verify_locations(self.config.server_config['ssl_path'] + '/'
                                  + self.config.server_config['ca_certificate'])

        reactor.listenSSL(self.config.server_config['port'], site, self.ssl_factory)

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



