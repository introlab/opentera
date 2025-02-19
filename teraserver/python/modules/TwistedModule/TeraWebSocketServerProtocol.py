# WebSockets
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.exception import Disconnected
from autobahn.websocket.types import ConnectionDeny

# OpenTera
from opentera.redis.RedisClient import RedisClient
from opentera.logging.LoggingClient import LoggingClient

# Messages
import opentera.messages.python as messages
import datetime
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse, ParseError
from google.protobuf.message import DecodeError


# Twisted
from twisted.internet import defer


class TeraWebSocketServerProtocol(WebSocketServerProtocol, RedisClient):
    def __init__(self, config):
        RedisClient.__init__(self, config=config)
        WebSocketServerProtocol.__init__(self)

        self.logger = LoggingClient(config, 'LoggingClient_' + self.__class__.__name__)
        self.event_manager = None
        self.registered_events = set()  # Collection of unique elements

    def onOpen(self):
        print(type(self).__name__, 'TeraWebSocketServerProtocol - onOpen')
        # Moved handling code in redisConnectionMade...
        # because it always occurs after onOpen...

    def onClose(self, wasClean, code, reason):
        print(type(self).__name__, 'TeraWebSocketServerProtocol - onClose')
        self.redisClose()
        self.logger.close()

    def onPong(self, payload):
        # print('onPong', payload)
        # Should we do something?
        pass

    def onMessage(self, msg, binary):
        # Handle websocket communication
        print('TeraWebSocketServerProtocol - onMessage (websocket in)', self, msg, binary)
        self.sendMessage(str('Not allowed to send message').encode('utf-8'), False)

    def onOpenHandshakeTimeout(self):
        print('TeraWebSocketServerProtocol - onOpenHandshakeTimeout', self)

    def onCloseHandshakeTimeout(self):
        print('TeraWebSocketServerProtocol - onCloseHandshakeTimeout', self)

    def onServerConnectionDropTimeout(self):
        print('TeraWebSocketServerProtocol - onServerConnectionDropTimeout', self)

    def redis_tera_module_message_received(self, pattern, channel, message):
        # print('TeraWebSocketServerProtocol - redis_tera_module_message_received', pattern, channel, message)
        try:
            tera_module_message = messages.TeraModuleMessage()
            if isinstance(message, str):
                ret = tera_module_message.ParseFromString(message.encode('utf-8'))
            elif isinstance(message, bytes):
                ret = tera_module_message.ParseFromString(message)

            for any_message in tera_module_message.data:
                # Look for server command
                server_command = messages.ServerCommand()

                if any_message.Unpack(server_command):
                    if server_command.type == messages.ServerCommand.CMD_CLIENT_DISCONNECT:
                        self.sendClose(4000, 'CMD_CLIENT_DISCONNECT')

        except DecodeError as d:
            print('TeraWebSocketServerProtocol - DecodeError ', pattern, channel, message, d)
        except ParseError as e:
            print('TeraWebSocketServerProtocol - Failure in redisMessageReceived', e)

    def redis_event_message_received(self, pattern, channel, message):
        # print('TeraWebSocketServerProtocol - redis_event_message_received', pattern, channel, message)
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
                    json = MessageToJson(tera_message, always_print_fields_with_no_presence=True)

                    # Send to websocket (not in binary form)
                    self.sendMessage(json.encode('utf-8'), False)

        except DecodeError as d:
            print('TeraWebSocketServerProtocol - DecodeError ', pattern, channel, message, d)
        except ParseError as e:
            print('TeraWebSocketServerProtocol - Failure in redisMessageReceived', e)
        except Disconnected as e:
            print('TeraWebSocketServerProtocol - Sending message on closed socket.', e)

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

    def event_topic(self):
        return ''

    def send_event_message(self, event, topic: str):
        message = self.create_event_message(topic)
        any_message = messages.Any()
        any_message.Pack(event)
        message.events.extend([any_message])
        self.publish(message.header.topic, message.SerializeToString())

    def create_event_message(self, topic):
        event_message = messages.TeraEvent()
        event_message.header.version = 1
        event_message.header.time = datetime.datetime.now().timestamp()
        event_message.header.topic = topic
        return event_message
