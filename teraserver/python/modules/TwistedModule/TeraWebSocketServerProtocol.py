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
from messages.python.UserDisconnected_pb2 import UserDisconnected
from messages.python.Result_pb2 import Result
from google.protobuf.any_pb2 import Any
import datetime
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse, ParseError
from google.protobuf.message import DecodeError

# Twisted
from twisted.internet import defer


class TeraWebSocketServerProtocol(RedisClient, WebSocketServerProtocol):

    def __init__(self, config):
        RedisClient.__init__(self, config=config)
        WebSocketServerProtocol.__init__(self)
        self.user = None
        self.participant = None

    @defer.inlineCallbacks
    def redisConnectionMade(self):
        print('TeraWebSocketServerProtocol redisConnectionMade (redis)')

        # This will wait until subscribe result is available...
        ret = yield self.subscribe(self.answer_topic())

        if self.user:
            # Advertise that we have a new user
            tera_message = self.create_tera_message(create_module_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            user_connected = UserConnected()
            user_connected.user_uuid = str(self.user.user_uuid)

            # Need to use Any container
            any_message = Any()
            any_message.Pack(user_connected)
            tera_message.data.extend([any_message])

            # Publish to login module (bytes)
            self.publish(create_module_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                         tera_message.SerializeToString())
        elif self.participant:
            # TODO Advertise that we have a new participant
            pass

    def onMessage(self, msg, binary):
        # Handle websocket communication
        # TODO use protobuf ?
        print('TeraWebSocketProtocol onMessage', self, msg, binary)

        # Parse JSON (protobuf content)
        try:
            message = Parse(msg, TeraMessage)
            self.publish(message.head.dest, message)
        except ParseError:
            print('TeraMessage parse error...')

        # Echo for debug
        self.sendMessage(msg, binary)

    def redisMessageReceived(self, pattern, channel, message):
        print('TeraWebSocketServerProtocol redis message received', pattern, channel, message)

        # Forward as JSON to websocket
        try:
            tera_message = TeraMessage()
            if isinstance(message, str):
                tera_message.ParseFromString(message.encode('utf-8'))
            elif isinstance(message, bytes):
                tera_message.ParseFromString(message)

            # Test message to JSON
            json = MessageToJson(tera_message, including_default_value_fields=True)

            # Send to websocket (in binary form)
            self.sendMessage(json.encode('utf-8'), False)

        except DecodeError:
            print('DecodeError ', pattern, channel, message)
            self.sendMessage(message.encode('utf-8'), False)
        except:
            print('Failure in redisMessageReceived')

    def onConnect(self, request):
        """
        Cannot send message at this stage, needs to verify connection here.
        """
        print('onConnect')

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
        print(type(self).__name__, 'onOpen')
        # Moved handling code in redisConnectionMade...
        # because it always occurs after onOpen...

    def onClose(self, wasClean, code, reason):
        if self.user:
            # Advertise that user disconnected
            tera_message = self.create_tera_message(create_module_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            user_disconnected = UserDisconnected()
            user_disconnected.user_uuid = str(self.user.user_uuid)

            # Need to use Any container
            any_message = Any()
            any_message.Pack(user_disconnected)
            tera_message.data.extend([any_message])

            # Publish to login module (bytes)
            self.publish(create_module_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                         tera_message.SerializeToString())

        elif self.participant:
            # TODO advertise that participant leaved
            pass

        print('onClose', self, wasClean, code, reason)

    def onOpenHandshakeTimeout(self):
        print('onOpenHandshakeTimeout', self)

    def answer_topic(self):
        if self.user:
            return 'websocket.user.' + self.user.user_uuid
        if self.participant:
            return 'websocket.participant.' + self.participant.participant_uuid

    def create_tera_message(self, dest='', seq=0):

        tera_message = TeraMessage()
        tera_message.head.version = 1
        tera_message.head.time = datetime.datetime.now().timestamp()
        tera_message.head.seq = seq
        tera_message.head.source = self.answer_topic()
        tera_message.head.dest = dest
        return tera_message
