# WebSockets
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.websocket.types import ConnectionRequest, ConnectionResponse, ConnectionDeny

# OpenTera
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.redis.RedisClient import RedisClient


class TeraWebSocketServerProtocol(WebSocketServerProtocol, RedisClient):

    def __init__(self, config):
        WebSocketServerProtocol.__init__(self)
        RedisClient.__init__(self, config=config)
        self.user = None
        self.participant = None

    def redisConnectionMade(self):
        print('TeraWebSocketServerProtocol redisConnectionMade (redis)')

        if self.user:
            # Subscribe to our own messages
            self.subscribe('server.' + str(self.user.user_uuid) + '.*')
        if self.participant:
            # Subscribe to our own messages
            self.subscribe('server.' + str(self.participant.participant_uuid) + '.*')

    def onMessage(self, msg, binary):
        print('TeraWebSocketProtocol onMessage', self, msg, binary)

        if self.user:
            self.publish('websocket.' + str(self.user.user_uuid) + '.request', msg)

        if self.participant:
            self.publish('websocket.' + str(self.participant.participant_uuid) + '.request', msg)

        # Echo for debug
        self.sendMessage(msg, binary)

    def redisMessageReceived(self, pattern, channel, message):
        print('TeraWebSocketServerProtocol redis message received', pattern, channel, message)
        self.sendMessage(message.encode('utf-8'), False)

    def onConnect(self, request):
        """
        Cannot send message at this stage, needs to verify connection here.
        """
        print('onConnect', self, request)

        if request.params.__contains__('id'):

            # Look for id in
            id = request.params['id']
            print('testing id: ', id)

            value = self.redisGet(id[0])

            if value is not None:
                # Needs to be converted from bytes to string to work
                user_uuid = value.decode("utf-8")
                print('user uuid ', user_uuid)

                # User verification
                self.user = TeraUser.get_user_by_uuid(user_uuid)
                if self.user is not None:
                    # Remove key
                    print('OK! removing key')
                    self.redisDelete(id[0])
                    return

        if request.params.__contains__('token'):

            # Look for token
            token = request.params['token']
            print('testing token: ', token)

            self.participant = TeraParticipant.get_participant_by_token(token[0])

            if self.participant is not None:
                print('Participant connected ', self.participant)
                return

        # if we get here we need to close the websocket, auth failed.
        # To deny a connection, raise an Exception
        raise ConnectionDeny(ConnectionDeny.FORBIDDEN, "Websocket authentication failed (key, uuid).")

    def onOpen(self):
        if self.user:
            # Advertise that we have a new user
            self.publish('websocket.' + str(self.user.user_uuid), 'connected')
            # At this stage, we can send messages. initiating...
            self.sendMessage(bytes('Hello ' + str(self.user), 'utf-8'), False)
        elif self.participant:
            # Advertise that we have a new user
            self.publish('websocket.' + str(self.participant.participant_uuid), 'connected')
            # At this stage, we can send messages. initiating...
            self.sendMessage(bytes('Hello ' + str(self.participant), 'utf-8'), False)

    def onClose(self, wasClean, code, reason):
        if self.user:
            self.publish('websocket.' + str(self.user.user_uuid), 'disconnected')
        elif self.participant:
            self.publish('websocket.' + str(self.participant.participant_uuid), 'disconnected')

        print('onClose', self, wasClean, code, reason)

    def onOpenHandshakeTimeout(self):
        print('onOpenHandshakeTimeout', self)
