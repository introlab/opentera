# WebSockets
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.websocket.types import ConnectionRequest, ConnectionResponse, ConnectionDeny

# OpenTera
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.redis.RedisClient import RedisClient
from modules.BaseModule import ModuleNames, create_module_topic_from_name


# Messages
from messages.python.TeraMessage_pb2 import TeraMessage
from messages.python.UserConnected_pb2 import UserConnected
from google.protobuf.any_pb2 import Any
import datetime

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
        # Handle websocket communication
        # TODO use protobuf ?
        print('TeraWebSocketProtocol onMessage', self, msg, binary)

        if self.user:
            self.publish('websocket.' + str(self.user.user_uuid) + '.request', msg)

        if self.participant:
            self.publish('websocket.' + str(self.participant.participant_uuid) + '.request', msg)

        # Echo for debug
        self.sendMessage(msg, binary)

    def redisMessageReceived(self, pattern, channel, message):
        print('TeraWebSocketServerProtocol redis message received', pattern, channel, message)
        # TODO use protobuf ?
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
            tera_message = TeraMessage()
            protobuf_message = UserConnected()
            protobuf_message.user_uuid = str(self.user.user_uuid)
            protobuf_message.reply_to = self.answer_topic()

            """
                message Header {
                    uint32 version = 1;
                    int64 time = 2;
                    uint32 seq = 3;
                    string source = 4;
                    string dest = 5;
                }
            
                Header head = 1;
            
                repeated google.protobuf.Any data = 2;
            """

            # TODO too complicated....
            tera_message.head.version = 1
            # tera_message.head.time = datetime.datetime.now().timestamp()
            # tera_message.head.seq = 0
            tera_message.head.source = self.answer_topic()
            tera_message.head.dest = create_module_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME)

            any_message = Any()
            any_message.Pack(protobuf_message)
            tera_message.data.extend([any_message])

            # Publish to login module (bytes)
            self.publish(create_module_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                         tera_message.SerializeToString())

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

    def answer_topic(self):
        if self.user:
            return 'websocket.user.' + self.user.user_uuid
        if self.participant:
            return 'websocket.participant.' + self.participant.participant_uuid