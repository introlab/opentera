# WebSockets
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.websocket.types import ConnectionRequest, ConnectionResponse, ConnectionDeny

# OpenTera
from libtera.db.models.TeraUser import TeraUser
from libtera.redis.RedisClient import RedisClient
from modules.BaseModule import ModuleNames, create_module_topic_from_name


# Messages
from messages.python.TeraMessage_pb2 import TeraMessage
from messages.python.UserEvent_pb2 import UserEvent
from messages.python.JoinSessionEvent_pb2 import JoinSessionEvent
from google.protobuf.any_pb2 import Any
import datetime
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse, ParseError
from google.protobuf.message import DecodeError

# Twisted
from twisted.internet import defer


class TeraWebSocketServerUserProtocol(RedisClient, WebSocketServerProtocol):

    def __init__(self, config):
        RedisClient.__init__(self, config=config)
        WebSocketServerProtocol.__init__(self)
        self.user = None

    @defer.inlineCallbacks
    def redisConnectionMade(self):
        print('TeraWebSocketServerUserProtocol redisConnectionMade (redis)')

        # This will wait until subscribe result is available...
        ret = yield self.subscribe(self.answer_topic())

        if self.user:
            # Advertise that we have a new user
            tera_message = self.create_tera_message(create_module_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            user_connected = UserEvent()
            user_connected.user_uuid = str(self.user.user_uuid)
            user_connected.type = UserEvent.USER_CONNECTED
            # Need to use Any container
            any_message = Any()
            any_message.Pack(user_connected)
            tera_message.data.extend([any_message])

            # Publish to login module (bytes)
            self.publish(create_module_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                         tera_message.SerializeToString())

    def onMessage(self, msg, binary):
        # Handle websocket communication
        # TODO use protobuf ?
        print('TeraWebSocketServerUserProtocol onMessage', self, msg, binary)

        if binary:
            # Decode protobuf before parsing
            pass

        # Parse JSON (protobuf content)
        try:
            message = Parse(msg, TeraMessage)
            self.publish(message.head.dest, message)
        except ParseError:
            print('TeraWebSocketServerUserProtocol - TeraMessage parse error...')

        # Echo for debug
        self.sendMessage(msg, binary)

    def redisMessageReceived(self, pattern, channel, message):
        print('TeraWebSocketServerUserProtocol redis message received', pattern, channel, message)

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
            print('TeraWebSocketServerUserProtocol - DecodeError ', pattern, channel, message)
            self.sendMessage(message.encode('utf-8'), False)
        except:
            print('TeraWebSocketServerUserProtocol - Failure in redisMessageReceived')

    def onConnect(self, request):
        """
        Cannot send message at this stage, needs to verify connection here.
        """
        print('TeraWebSocketServerUserProtocol - onConnect')

        if request.params.__contains__('id'):

            # Look for session id in
            my_id = request.params['id']
            print('TeraWebSocketServerUserProtocol - testing id: ', my_id)

            value = self.redisGet(my_id[0])

            if value is not None:
                # Needs to be converted from bytes to string to work
                user_uuid = value.decode("utf-8")
                print('TeraWebSocketServerUserProtocol - user uuid ', user_uuid)

                # User verification
                self.user = TeraUser.get_user_by_uuid(user_uuid)
                if self.user is not None:
                    # Remove key
                    print('TeraWebSocketServerUserProtocol - OK! removing key')
                    self.redisDelete(my_id[0])
                    return

        # if we get here we need to close the websocket, auth failed.
        # To deny a connection, raise an Exception
        raise ConnectionDeny(ConnectionDeny.FORBIDDEN,
                             "TeraWebSocketServerUserProtocol Websocket authentication failed (key, uuid).")

    def onOpen(self):
        print(type(self).__name__, 'TeraWebSocketServerUserProtocol - onOpen')
        # Moved handling code in redisConnectionMade...
        # because it always occurs after onOpen...

    def onClose(self, wasClean, code, reason):
        if self.user:
            # Advertise that user disconnected
            tera_message = self.create_tera_message(create_module_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            user_disconnected = UserEvent()
            user_disconnected.user_uuid = str(self.user.user_uuid)
            user_disconnected.type = UserEvent.USER_DISCONNECTED

            # Need to use Any container
            any_message = Any()
            any_message.Pack(user_disconnected)
            tera_message.data.extend([any_message])

            # Publish to login module (bytes)
            self.publish(create_module_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                         tera_message.SerializeToString())

        print('onClose', self, wasClean, code, reason)

    def onOpenHandshakeTimeout(self):
        print('TeraWebSocketServerUserProtocol - onOpenHandshakeTimeout', self)

    def answer_topic(self):
        if self.user:
            return 'websocket.user.' + self.user.user_uuid

    def create_tera_message(self, dest='', seq=0):

        tera_message = TeraMessage()
        tera_message.head.version = 1
        tera_message.head.time = datetime.datetime.now().timestamp()
        tera_message.head.seq = seq
        tera_message.head.source = self.answer_topic()
        tera_message.head.dest = dest
        return tera_message
