from autobahn.twisted.websocket import WebSocketServerFactory


# Factory wrapper, using redis configuration
class TwistedModuleWebSocketServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        # Get the argument for this class, then continue with init on base class
        self.config = kwargs.pop('redis_config', None)
        WebSocketServerFactory.__init__(self, *args, **kwargs)

        # Manage automatic ping/pong to make sure connection persists though proxy
        # Values are in seconds
        self.setProtocolOptions(autoPingInterval=10, autoPingTimeout=30, autoPingSize=20)

    def __del__(self):
        print("****- Deleting TwistedModuleWebSocketServerFactory")

    def buildProtocol(self, addr):
        """
        This overloaded function is called when a new protocol (effective connection to the websocket server) is
        performed.
        :param addr:
        :return:
        """
        print("buildProtocol for : ", addr, self.protocol)
        p = self.protocol(config=self.config)

        # Avoid serving web page if connexion is not a websocket
        # Will return status code 426 Upgrade Required
        p.webStatus = False

        p.factory = self
        return p
