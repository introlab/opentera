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
from messages.python.UserEvent_pb2 import UserEvent
from google.protobuf.any_pb2 import Any
import datetime
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse, ParseError
from google.protobuf.message import DecodeError

# Twisted
from twisted.internet import defer


class TeraWebSocketServerParticipantProtocol(RedisClient, WebSocketServerProtocol):

    def __init__(self, config):
        RedisClient.__init__(self, config=config)
        WebSocketServerProtocol.__init__(self)
        self.participant = None

    @defer.inlineCallbacks
    def redisConnectionMade(self):
        print('TeraWebSocketServerParticipantProtocol redisConnectionMade (redis)')

        # This will wait until subscribe result is available...
        ret = yield self.subscribe(self.answer_topic())

        if self.participant:
            # TODO Advertise that we have a new participant
            pass

    def onMessage(self, msg, binary):
        # Handle websocket communication
        # TODO use protobuf ?
        print('TeraWebSocketServerParticipantProtocol onMessage', self, msg, binary)

        if binary:
            # Decode protobuf before parsing

            pass

        # Parse JSON (protobuf content)
        try:
            message = Parse(msg, TeraMessage)
            self.publish(message.head.dest, message)
        except ParseError:
            print('TeraWebSocketServerParticipantProtocol - TeraMessage parse error...')

        # Echo for debug
        self.sendMessage(msg, binary)

    def redisMessageReceived(self, pattern, channel, message):
        print('TeraWebSocketServerParticipantProtocol redis message received', pattern, channel, message)

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
            print('TeraWebSocketServerParticipantProtocol - DecodeError ', pattern, channel, message)
            self.sendMessage(message.encode('utf-8'), False)
        except:
            print('TeraWebSocketServerParticipantProtocol - Failure in redisMessageReceived')

    def onConnect(self, request):
        """
        Cannot send message at this stage, needs to verify connection here.
        """
        print('onConnect')

        if request.params.__contains__('token'):

            # Look for token
            token = request.params['token']
            print('TeraWebSocketServerParticipantProtocol - testing token: ', token)

            self.participant = TeraParticipant.get_participant_by_token(token[0])

            if self.participant is not None:
                print('TeraWebSocketServerParticipantProtocol - Participant connected ', self.participant)
                return

        # if we get here we need to close the websocket, auth failed.
        # To deny a connection, raise an Exception
        raise ConnectionDeny(ConnectionDeny.FORBIDDEN,
                             "TeraWebSocketServerParticipantProtocol - Websocket authentication failed (key, uuid).")

    def onOpen(self):
        print(type(self).__name__, 'TeraWebSocketServerParticipantProtocol - onOpen')
        # Moved handling code in redisConnectionMade...
        # because it always occurs after onOpen...

    def onClose(self, wasClean, code, reason):
        if self.participant:
            # TODO advertise that participant leaved
            pass

        print('TeraWebSocketServerParticipantProtocol - onClose', self, wasClean, code, reason)

    def onOpenHandshakeTimeout(self):
        print('TeraWebSocketServerParticipantProtocol - onOpenHandshakeTimeout', self)

    def answer_topic(self):
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

