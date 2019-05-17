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
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.python import log

import sys


class TwistedModule(BaseModule):

    def __init__(self, config: ConfigManager):

        BaseModule.__init__(self, ModuleNames.TWISTED_MODULE_NAME.value, config)

        print('setup_twisted')

        # create a Twisted Web resource for our WebSocket server
        # TODO Server IP should be stored in config
        wss_factory = TwistedModuleWebSocketServerFactory(u"wss://%s:%d" % ('localhost',
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
        site = Site(root_resource)

        # setup an application for serving the site
        # web_service = internet.TCPServer(settings.PORT, site, interface=settings.INTERFACE)
        # application = service.Application(__name__)
        # web_service.setServiceParent(application)

        reactor.listenSSL(self.config.server_config['port'], site,
                          ssl.DefaultOpenSSLContextFactory(privateKeyFileName=
                                                           self.config.server_config['ssl_path'] + '/key.pem',
                                                           certificateFileName=
                                                           self.config.server_config['ssl_path'] + '/cert.crt'))
        print('setup_twisted done')

    def __del__(self):
        pass

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



