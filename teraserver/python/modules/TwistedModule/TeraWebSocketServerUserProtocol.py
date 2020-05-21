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


class TeraWebSocketServerUserProtocol(RedisClient, WebSocketServerProtocol):

    def __init__(self, config):
        RedisClient.__init__(self, config=config)
        WebSocketServerProtocol.__init__(self)
        self.user = None
        self.event_manager = None
        self.registered_events = set()  # Collection of unique elements

    @defer.inlineCallbacks
    def redisConnectionMade(self):
        print('TeraWebSocketServerUserProtocol redisConnectionMade (redis)')

        # This will wait until subscribe result is available...
        # Subscribe to messages to the websocket
        # TODO, Still useful?
        # ret = yield self.subscribe(self.answer_topic())
        ret = yield self.subscribe_pattern_with_callback(self.answer_topic(), self.redis_tera_message_received)
        print(ret)

        if self.user:
            # Advertise that we have a new user
            tera_message = self.create_tera_message(
                create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            user_connected = messages.UserEvent()
            user_connected.user_uuid = str(self.user.user_uuid)
            user_connected.type = messages.UserEvent.USER_CONNECTED
            # Need to use Any container
            any_message = messages.Any()
            any_message.Pack(user_connected)
            tera_message.data.extend([any_message])

            # Publish to UserManager module (bytes)
            self.publish(create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                         tera_message.SerializeToString())

            # This will wait until subscribe result is available...
            # Register only once to events from modules, will be filtered after
            # ret = yield self.subscribe(create_module_event_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            ret = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.USER_MANAGER_MODULE_NAME), self.redis_event_message_received)
            print(ret)
            ret = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.DATABASE_MODULE_NAME), self.redis_event_message_received)
            print(ret)

    def onMessage(self, msg, binary):
        # Handle websocket communication
        # TODO use protobuf ?
        print('TeraWebSocketServerUserProtocol onMessage', self, msg, binary)

        if binary:
            # Decode protobuf before parsing
            return

        try:
            # Parse JSON (protobuf content)
            message = Parse(msg, messages.TeraModuleMessage())

            # Verify if the message if for us (register message)
            if message.head.dest == self.answer_topic():
                # Test if we have a register message
                for any_msg in message.data:
                    register_event = messages.UserRegisterToEvent()
                    result = messages.Result()
                    if any_msg.Unpack(register_event):
                        if register_event.action == messages.UserRegisterToEvent.ACTION_REGISTER:
                            self.registered_events.add(register_event.event_type)
                            result.type = messages.Result.RESULT_OK
                            result.code = 0
                            result.message = 'Registered to :' + str(register_event)

                        elif register_event.action == messages.UserRegisterToEvent.ACTION_UNREGISTER:
                            self.registered_events.remove(register_event.event_type)
                            result.type = messages.Result.RESULT_OK
                            result.code = 0
                            result.message = 'Unregistered to :' + str(register_event)
                        else:
                            print('Unknown action: ', register_event.action)
                            result.type = messages.Result.RESULT_ERROR
                            result.code = -1
                            result.message = 'Unknown event type : ' + str(register_event)

                        # Done, do not forward UserRegisterToEvent
                        answer = self.create_tera_message(dest=message.head.source)

                        any_message = messages.Any()
                        any_message.Pack(result)
                        answer.data.extend([any_message])

                        tera_message = messages.TeraMessage()
                        tera_message.message.Pack(answer)

                        json_data = MessageToJson(tera_message, including_default_value_fields=True)

                        # Send to websocket (in byte form)
                        self.sendMessage(json_data.encode('utf-8'), False)
            else:
                # Message not for us
                # NOT sure we should forward messages to anything...
                # self.publish(message.head.dest, message)
                pass
        except ParseError as e:
            print('TeraWebSocketServerUserProtocol - TeraModuleMessage parse error...', e)

        # Echo for debug
        # self.sendMessage(msg, binary)

    def redis_tera_message_received(self, pattern, channel, message):
        print('redis_tera_message_received', pattern, channel, message)

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
            print('TeraWebSocketServerUserProtocol - DecodeError ', pattern, channel, message, d)
        except ParseError as e:
            print('TeraWebSocketServerUserProtocol - Failure in redisMessageReceived', e)

    def redis_event_message_received(self, pattern, channel, message):
        print('redis_event_message_received', pattern, channel, message)
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
            print('TeraWebSocketServerUserProtocol - DecodeError ', pattern, channel, message, d)
        except ParseError as e:
            print('TeraWebSocketServerUserProtocol - Failure in redisMessageReceived', e)

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

                    # Create event manager
                    self.event_manager = UserEventManager(self.user)

                    return

        # if we get here we need to close the websocket, auth failed.
        # To deny a connection, raise an Exception
        raise ConnectionDeny(ConnectionDeny.FORBIDDEN,
                             "TeraWebSocketServerUserProtocol Websocket authentication failed (key, uuid).")

    def onOpen(self):
        print(type(self).__name__, 'TeraWebSocketServerUserProtocol - onOpen')
        # Moved handling code in redisConnectionMade...
        # because it always occurs after onOpen...

    @defer.inlineCallbacks
    def onClose(self, wasClean, code, reason):
        if self.user:
            # Advertise that user disconnected
            tera_message = self.create_tera_message(
                create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            user_disconnected = messages.UserEvent()
            user_disconnected.user_uuid = str(self.user.user_uuid)
            user_disconnected.type = messages.UserEvent.USER_DISCONNECTED

            # Need to use Any container
            any_message = messages.Any()
            any_message.Pack(user_disconnected)
            tera_message.data.extend([any_message])

            # Publish to login module (bytes)
            self.publish(create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                         tera_message.SerializeToString())

            # Unsubscribe to events
            # ret = yield self.unsubscribe(create_module_event_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            ret = yield self.unsubscribe_pattern_with_callback(
                create_module_event_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                self.redis_event_message_received)
            print(ret)

        # Unsubscribe to messages
        # ret = yield self.unsubscribe(self.answer_topic())
        ret = yield self.unsubscribe_pattern_with_callback(self.answer_topic(), self.redis_tera_message_received)
        print(ret)

        print('onClose', self, wasClean, code, reason)

    def onOpenHandshakeTimeout(self):
        print('TeraWebSocketServerUserProtocol - onOpenHandshakeTimeout', self)

    def answer_topic(self):
        if self.user:
            return 'websocket.user.' + self.user.user_uuid

    def create_tera_message(self, dest='', seq=0):

        tera_message = messages.TeraModuleMessage()
        tera_message.head.version = 1
        tera_message.head.time = datetime.datetime.now().timestamp()
        tera_message.head.seq = seq
        tera_message.head.source = self.answer_topic()
        tera_message.head.dest = dest
        return tera_message
