from modules.FlaskModule import flask_app

# WebSockets
from autobahn.twisted.resource import WebSocketResource, WSGIRootResource
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.websocket.types import ConnectionRequest, ConnectionResponse, ConnectionDeny

# Twisted
from twisted.application import internet, service
from twisted.internet import reactor, ssl
from twisted.python.threadpool import ThreadPool
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.python import log


import sys

from modules.RedisModule import get_redis
from libtera.db.models.TeraUser import TeraUser
import uuid

from libtera.redis.RedisProtocolFactory import RedisProtocolFactory, redisProtocol
from libtera.redis.RedisClient import RedisClient

# Event based, twisted redis
import txredisapi as txredis


class TwistedModule:

    def __init__(self, server_config):
        print('setup_twisted')

        # create a Twisted Web resource for our WebSocket server
        wss_factory = WebSocketServerFactory(u"wss://%s:%d" % ('localhost', server_config['port']))
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

        reactor.listenSSL(server_config['port'], site,
                          ssl.DefaultOpenSSLContextFactory(privateKeyFileName=server_config['ssl_path'] + '/key.pem',
                                                           certificateFileName=server_config['ssl_path'] + '/cert.crt'))
        print('setup_twisted done')

    def callInThread(self, f, name):
        reactor.callInThread(f, name)

    def run(self):
        log.startLogging(sys.stdout)
        reactor.run()


class TeraWebSocketServerProtocol(WebSocketServerProtocol, RedisClient):

    def __init__(self):
        WebSocketServerProtocol.__init__(self)
        RedisClient.__init__(self)
        self.user = None

    def redisConnectionMade(self):
        print('TeraWebSocketServerProtocol redisConnectionMade (redis)')

        # Subscribe to our own messages
        self.subscribe('server.' + str(self.user.user_uuid) + '.answer')

    def onMessage(self, msg, binary):
        print('TeraWebSocketProtocol onMessage', self, msg, binary)

        get_redis().publish('websocket.' + str(self.user.user_uuid) + '.request', msg)

        # Echo
        self.sendMessage(msg, binary)

    def redisMessageReceived(self, pattern, channel, message):
        print('TeraWebSocketServerProtocol redis message received', pattern, channel, message)
        self.sendMessage(message.encode('utf-8'), False)

    def onConnect(self, request):
        """
        Cannot send message at this stage, needs to verify connection here.
        """
        print('onConnect', self, request)

        # Look for id in
        id = request.params['id']
        red = get_redis()

        print('testing id: ', id)

        if red is not None and len(id) > 0:

            value = red.get(id[0])

            if value is not None:
                # Needs to be converted from bytes to string to work
                user_uuid = value.decode("utf-8")
                print('user uuid ', user_uuid)

                # User verification
                self.user = TeraUser.get_user_by_uuid(user_uuid)
                if self.user is not None:
                    # Remove key
                    print('OK! removing key')
                    red.delete(id[0])
                    return

        # if we get here we need to close the websocket, auth failed.
        # To deny a connection, raise an Exception
        raise ConnectionDeny(ConnectionDeny.FORBIDDEN, "Websocket authentication failed (key, uuid).")

    def onOpen(self):
        # Advertise that we have a new user
        get_redis().publish('websocket.' + str(self.user.user_uuid), 'connected')
        # At this stage, we can send messages. initiating...
        self.sendMessage(bytes('Hello ' + str(self.user), 'utf-8'), False)

    def onClose(self, wasClean, code, reason):
        get_redis().publish('websocket.' + str(self.user.user_uuid), 'disconnected')
        print('onClose', self, wasClean, code, reason)

    def onOpenHandshakeTimeout(self):
        print('onOpenHandshakeTimeout', self)
