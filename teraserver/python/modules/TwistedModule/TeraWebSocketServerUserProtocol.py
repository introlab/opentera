# WebSockets
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.websocket.types import ConnectionDeny

# OpenTera
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraAsset import TeraAsset

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

from modules.TwistedModule.TeraWebSocketServerProtocol import TeraWebSocketServerProtocol


class TeraWebSocketServerUserProtocol(TeraWebSocketServerProtocol):

    def __init__(self, config):
        TeraWebSocketServerProtocol.__init__(self, config=config)
        self.user = None

    @defer.inlineCallbacks
    def redisConnectionMade(self):
        print('TeraWebSocketServerUserProtocol redisConnectionMade (redis)')

        # This will wait until subscribe result is available...
        # Subscribe to messages to the websocket
        # ret = yield self.subscribe_pattern_with_callback(self.answer_topic(), self.redis_tera_message_received)
        # print(ret)

        if self.user:
            # Advertise that we have a new user
            tera_message = self.create_tera_message(
                create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            user_connected = messages.UserEvent()
            user_connected.user_uuid = str(self.user.user_uuid)
            user_connected.user_fullname = self.user.get_fullname()
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

            # Events from UserManagerModule
            ret1 = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.USER_MANAGER_MODULE_NAME), self.redis_event_message_received)

            # Specific events from DatabaseModule
            # We are specific otherwise we receive every database event
            ret2 = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.DATABASE_MODULE_NAME, TeraUser.get_model_name()), self.redis_event_message_received)

            ret3 = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.DATABASE_MODULE_NAME, TeraParticipant.get_model_name()), self.redis_event_message_received)

            ret4 = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.DATABASE_MODULE_NAME, TeraDevice.get_model_name()), self.redis_event_message_received)

            ret5 = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.DATABASE_MODULE_NAME, TeraAsset.get_model_name()), self.redis_event_message_received)

            # Direct events
            ret6 = yield self.subscribe_pattern_with_callback(self.event_topic(), self.redis_event_message_received)

            print(ret1, ret2, ret3, ret4, ret5, ret6)

    def onMessage(self, msg, binary):
        # Handle websocket communication
        # TODO use protobuf ?
        print('TeraWebSocketServerUserProtocol onMessage (websocket in)', self, msg, binary)

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
            ret1 = yield self.unsubscribe_pattern_with_callback(
                create_module_event_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                self.redis_event_message_received)

            ret2 = yield self.unsubscribe_pattern_with_callback(
                create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME),
                self.redis_event_message_received)

            ret3 = yield self.unsubscribe_pattern_with_callback(self.event_topic(), self.redis_event_message_received)

            print(ret1, ret2, ret3)

        # Unsubscribe to messages
        # ret = yield self.unsubscribe_pattern_with_callback(self.answer_topic(), self.redis_tera_message_received)
        # print(ret)

        print('onClose', self, wasClean, code, reason)

    def answer_topic(self):
        if self.user:
            return 'websocket.user.' + self.user.user_uuid
        return super().answer_topic()

    def event_topic(self):
        if self.user:
            return 'websocket.user.' + self.user.user_uuid + '.events'
        return super().event_topic()
