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
        print('TeraWebSocketServerUserProtocol - redisConnectionMade (redis)', self)

        # This will wait until subscribe result is available...
        # Subscribe to messages to the websocket
        # ret = yield self.subscribe_pattern_with_callback(self.answer_topic(), self.redis_tera_message_received)
        # print(ret)

        if self.user:
            # This will wait until subscribe result is available...
            # Register only once to events from modules, will be filtered after

            # Events from UserManagerModule
            ret = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.USER_MANAGER_MODULE_NAME), self.redis_event_message_received)

            # Specific events from DatabaseModule
            # We are specific otherwise we receive every database event
            from libtera.db.models import EventNameClassMap

            for name in EventNameClassMap:
                ret = yield self.subscribe_pattern_with_callback(
                    create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME, name),
                    self.redis_event_message_received)

            # Direct events
            ret = yield self.subscribe_pattern_with_callback(self.event_topic(), self.redis_event_message_received)

            # MAKE SURE TO SUBSCRIBE TO EVENTS BEFORE SENDING ONLINE MESSAGE
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

    def onConnect(self, request):
        """
        Cannot send message at this stage, needs to verify connection here.
        """
        print('TeraWebSocketServerUserProtocol - onConnect', self)

        if request.params.__contains__('id'):

            # Look for session id in
            my_id = request.params['id']
            print('TeraWebSocketServerUserProtocol - testing id: ', my_id, self)

            value = self.redisGet(my_id[0])

            if value is not None:
                # Needs to be converted from bytes to string to work
                user_uuid = value.decode("utf-8")
                print('TeraWebSocketServerUserProtocol - user uuid ', user_uuid, self)

                # User verification
                self.user = TeraUser.get_user_by_uuid(user_uuid)
                if self.user is not None:
                    # Remove key
                    print('TeraWebSocketServerUserProtocol - OK! removing key', self)
                    self.redisDelete(my_id[0])

                    # Create event manager
                    self.event_manager = UserEventManager(self.user)

                    # log information
                    self.logger.log_info(self, "User websocket connected", self.user.user_username, self.user.user_uuid)

                    return

        # if we get here we need to close the websocket, auth failed.
        # To deny a connection, raise an Exception
        raise ConnectionDeny(ConnectionDeny.FORBIDDEN,
                             "TeraWebSocketServerUserProtocol Websocket authentication failed (key, uuid).")

    @defer.inlineCallbacks
    def onClose(self, wasClean, code, reason):
        print('TeraWebSocketServerUserProtocol - onClose', self, wasClean, code, reason)
        if self.user:
            # Advertise that user disconnected
            tera_message = self.create_tera_message(
                create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            user_disconnected = messages.UserEvent()
            user_disconnected.user_uuid = str(self.user.user_uuid)
            user_disconnected.user_fullname = self.user.get_fullname()
            user_disconnected.type = messages.UserEvent.USER_DISCONNECTED

            # Need to use Any container
            any_message = messages.Any()
            any_message.Pack(user_disconnected)
            tera_message.data.extend([any_message])

            # Publish to login module (bytes)
            self.publish(create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                         tera_message.SerializeToString())

            # Unsubscribe to events
            ret = yield self.unsubscribe_pattern_with_callback(
                create_module_event_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                self.redis_event_message_received)

            # Specific events from DatabaseModule
            # We are specific otherwise we receive every database event
            from libtera.db.models import EventNameClassMap

            for name in EventNameClassMap:
                ret = yield self.unsubscribe_pattern_with_callback(
                    create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME, name),
                    self.redis_event_message_received)

            ret = yield self.unsubscribe_pattern_with_callback(self.event_topic(), self.redis_event_message_received)

            # log information
            self.logger.log_info(self, "User websocket disconnected", self.user.user_username, self.user.user_uuid)

        # Unsubscribe to messages
        # ret = yield self.unsubscribe_pattern_with_callback(self.answer_topic(), self.redis_tera_message_received)
        # print(ret)

    def answer_topic(self):
        if self.user:
            return 'websocket.user.' + self.user.user_uuid
        return super().answer_topic()

    def event_topic(self):
        if self.user:
            return 'websocket.user.' + self.user.user_uuid + '.events'
        return super().event_topic()
