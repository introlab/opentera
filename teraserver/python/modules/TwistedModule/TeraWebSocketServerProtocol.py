# WebSockets
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.websocket.types import ConnectionDeny

# OpenTera
from libtera.db.models.TeraUser import TeraUser
from libtera.redis.RedisClient import RedisClient
from modules.BaseModule import ModuleNames, create_module_message_topic_from_name, create_module_event_topic_from_name


# Messages
import messages.python as messages
import datetime
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse, ParseError
from google.protobuf.message import DecodeError

# Twisted
from twisted.internet import defer

# Event manager
from modules.UserEventManager import UserEventManager


class TeraWebSocketServerProtocol(RedisClient, WebSocketServerProtocol):
    def __init__(self, config):
        RedisClient.__init__(self, config=config)
        WebSocketServerProtocol.__init__(self)

        self.event_manager = None
        self.registered_events = set()  # Collection of unique elements

    def onOpen(self):
        print(type(self).__name__, 'TeraWebSocketServerProtocol - onOpen')
        # Moved handling code in redisConnectionMade...
        # because it always occurs after onOpen...

    def onOpenHandshakeTimeout(self):
        print('TeraWebSocketServerProtocol - onOpenHandshakeTimeout', self)

    def redis_tera_message_received(self, pattern, channel, message):
        print('TeraWebSocketServerProtocol - redis_tera_message_received', pattern, channel, message)

        # Forward as JSON to websocket
        try:
            tera_module_message = messages.TeraModuleMessage()
            if isinstance(message, str):
                ret = tera_module_message.ParseFromString(message.encode('utf-8'))
            elif isinstance(message, bytes):
                ret = tera_module_message.ParseFromString(message)

            # Conversion to generic message
            tera_message = messages.TeraMessage()
            tera_message.message.Pack(tera_module_message)

            # Converting to JSON
            json = MessageToJson(tera_message, including_default_value_fields=True)

            # Send to websocket (not in binary form)
            self.sendMessage(json.encode('utf-8'), False)

        except DecodeError as d:
            print('TeraWebSocketServerProtocol - DecodeError ', pattern, channel, message, d)
        except ParseError as e:
            print('TeraWebSocketServerProtocol - Failure in redisMessageReceived', e)

    def redis_event_message_received(self, pattern, channel, message):
        print('TeraWebSocketServerProtocol - redis_event_message_received', pattern, channel, message)
        # Forward as JSON to websocket
        try:
            event_message = messages.TeraEvent()
            if isinstance(message, str):
                ret = event_message.ParseFromString(message.encode('utf-8'))
            elif isinstance(message, bytes):
                ret = event_message.ParseFromString(message)

            if self.event_manager:
                # Filter events
                filtered_event_message = self.event_manager.filter_events(event_message)

                # Send if we still have events to send
                if filtered_event_message.events:
                    tera_message = messages.TeraMessage()
                    tera_message.message.Pack(filtered_event_message)

                    # Test message to JSON string
                    json = MessageToJson(tera_message, including_default_value_fields=True)

                    # Send to websocket (not in binary form)
                    self.sendMessage(json.encode('utf-8'), False)

        except DecodeError as d:
            print('TeraWebSocketServerProtocol - DecodeError ', pattern, channel, message, d)
        except ParseError as e:
            print('TeraWebSocketServerProtocol - Failure in redisMessageReceived', e)

    def create_tera_message(self, dest='', seq=0):
        tera_message = messages.TeraModuleMessage()
        tera_message.head.version = 1
        tera_message.head.time = datetime.datetime.now().timestamp()
        tera_message.head.seq = seq
        tera_message.head.source = self.answer_topic()
        tera_message.head.dest = dest
        return tera_message

    def answer_topic(self):
        return ''


