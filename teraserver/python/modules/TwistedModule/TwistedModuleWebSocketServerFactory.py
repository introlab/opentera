from autobahn.twisted.websocket import WebSocketServerFactory

# Same directory
from .TeraWebSocketServerProtocol import TeraWebSocketServerProtocol


# Factory wrapper, using redis configuration
class TwistedModuleWebSocketServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        # Get the argument for this class, then continue with init on base class
        self.config = kwargs.pop('redis_config', None)
        WebSocketServerFactory.__init__(self, *args, **kwargs)

    def buildProtocol(self, addr):
        """
        This overloaded function is called when a new protocol (effective connection to the websocket server) is
        performed.
        :param addr:
        :return:
        """
        p = TeraWebSocketServerProtocol(config=self.config)
        p.factory = self
        return p
