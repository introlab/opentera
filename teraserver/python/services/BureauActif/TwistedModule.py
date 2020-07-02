from .FlaskModule import flask_app
from modules.BaseModule import BaseModule, ModuleNames
from .ConfigManager import ConfigManager

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
import os


class MyHTTPChannel(HTTPChannel):
    def allHeadersReceived(self):
        # Verify if we have a client with a certificate...
        # cert = self.transport.getPeerCertificate()
        cert = getattr(self.transport, "getPeerCertificate", None)

        # Current request
        req = self.requests[-1]

        # SAFETY X-Device-UUID, X-Participant-UUID must not be set in header before testing certificate
        if req.requestHeaders.hasHeader('X-Device-UUID'):
            req.requestHeaders.removeHeader('X-Device-UUID')
            # TODO raise error?

        if req.requestHeaders.hasHeader('X-Participant-UUID'):
            req.requestHeaders.removeHeader('X-Participant-UUID')
            # TODO raise error ?

        if cert is not None:
            # Certificate found, add information in header
            subject = cert.get_subject()
            # Get UID if possible
            if 'Device' in subject.CN and hasattr(subject, 'UID'):
                user_id = subject.UID
                req.requestHeaders.addRawHeader('X-Device-UUID', user_id)
            if 'Participant' in subject.CN and hasattr(subject, 'UID'):
                user_id = subject.UID
                req.requestHeaders.addRawHeader('X-Participant-UUID', user_id)

        HTTPChannel.allHeadersReceived(self)


class MySite(Site):
    protocol = MyHTTPChannel

    def __init__(self, resource, requestFactory=None, *args, **kwargs):
        super().__init__(resource, requestFactory, *args, **kwargs)


class TwistedModule(BaseModule):

    def __init__(self, config: ConfigManager):

        # Warning, the name must be unique!
        BaseModule.__init__(self, 'BureauActifService.TwistedModule', config)

        # create a Twisted Web WSGI resource for our Flask server
        wsgi_resource = WSGIResource(reactor, reactor.getThreadPool(), flask_app)

        # create resource for static assets
        # static_resource = File(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'assets'))
        base_folder = os.path.dirname(os.path.abspath(__file__))
        static_resource = File(os.path.join(base_folder, 'static'))
        static_resource.contentTypes['.js'] = 'text/javascript'
        static_resource.forbidden = True

        # the path "/assets" served by our File stuff and
        root_resource = WSGIRootResource(wsgi_resource, {b'assets': static_resource})

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
        res1 = ctx.use_privatekey_file(os.path.join(
            os.path.abspath(self.config.service_config['ssl_path']),
            self.config.service_config['site_private_key']))

        res2 = ctx.use_certificate_file(os.path.join(
            os.path.abspath(self.config.service_config['ssl_path']),
            self.config.service_config['site_certificate']))

        # Certificate verification callback
        ctx.set_verify(SSL.VERIFY_NONE, self.verifyCallback)

        # With self-signed certs we have to explicitely tell the server to trust certificates
        ctx.load_verify_locations(os.path.join(
            os.path.abspath(self.config.service_config['ssl_path']),
            self.config.service_config['ca_certificate']))

        # reactor.listenSSL(self.config.service_config['port'], site, self.ssl_factory)
        reactor.listenTCP(self.config.service_config['port'], site)

    def __del__(self):
        pass

    def verifyCallback(self, connection, x509, errnum, errdepth, ok):
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
        print('BureauActifService.TwistedModule - Received message ', pattern, channel, message)
        pass

    def run(self):
        log.startLogging(sys.stdout)
        reactor.run()



