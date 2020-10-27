# WebSockets
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.websocket.types import ConnectionRequest, ConnectionResponse, ConnectionDeny

# OpenTera
from libtera.db.models.TeraDevice import TeraDevice
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
from modules.DeviceEventManager import DeviceEventManager

# Base class
from modules.TwistedModule.TeraWebSocketServerProtocol import TeraWebSocketServerProtocol


class TeraWebSocketServerDeviceProtocol(TeraWebSocketServerProtocol):

    def __init__(self, config):
        TeraWebSocketServerProtocol.__init__(self, config=config)
        self.device = None

    @defer.inlineCallbacks
    def redisConnectionMade(self):
        print('TeraWebSocketServerDeviceProtocol - redisConnectionMade (redis)', self)

        # This will wait until subscribe result is available...
        # ret = yield self.subscribe_pattern_with_callback(self.answer_topic(), self.redis_tera_message_received)
        # print(ret)

        if self.device:
            # This will wait until subscribe result is available...
            # Register only once to events from modules, will be filtered after
            ret1 = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.USER_MANAGER_MODULE_NAME), self.redis_event_message_received)

            ret2 = yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.DATABASE_MODULE_NAME), self.redis_event_message_received)

            # Direct events
            ret3 = yield self.subscribe_pattern_with_callback(self.event_topic(), self.redis_event_message_received)

            print(ret1, ret2, ret3)
            # MAKE SURE TO SUBSCRIBE TO EVENTS BEFORE SENDING ONLINE MESSAGE
            tera_message = self.create_tera_message(
                create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            device_connected = messages.DeviceEvent()
            device_connected.device_uuid = str(self.device.device_uuid)
            device_connected.device_name = self.device.device_name
            device_connected.type = messages.DeviceEvent.DEVICE_CONNECTED
            # Need to use Any container
            any_message = messages.Any()
            any_message.Pack(device_connected)
            tera_message.data.extend([any_message])

            # Publish to login module (bytes)
            self.publish(create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                         tera_message.SerializeToString())

    def onConnect(self, request):
        """
        Cannot send message at this stage, needs to verify connection here.
        """
        print('TeraWebSocketServerDeviceProtocol - onConnect', self)

        if request.params.__contains__('id'):
            # Look for session id in
            my_id = request.params['id']
            print('TeraWebSocketServerDeviceProtocol - testing id: ', my_id, self)

            value = self.redisGet(my_id[0])

            if value is not None:
                # Needs to be converted from bytes to string to work
                device_uuid = value.decode("utf-8")
                print('TeraWebSocketServerDeviceProtocol - device uuid ', device_uuid, self)

                # User verification
                self.device = TeraDevice.get_device_by_uuid(device_uuid)
                if self.device is not None:
                    # Remove key
                    print('TeraWebSocketServerDeviceProtocol - OK! removing key', self)
                    self.redisDelete(my_id[0])

                    # Create event manager
                    self.event_manager = DeviceEventManager(self.device)

                    # log information
                    self.logger.log_info(self, "Device websocket connected",
                                         self.device.device_name, self.device.device_uuid)

                    return

        # if we get here we need to close the websocket, auth failed.
        # To deny a connection, raise an Exception
        raise ConnectionDeny(ConnectionDeny.FORBIDDEN,
                             "TeraWebSocketServerDeviceProtocol - Websocket authentication failed (key, uuid).")

    @defer.inlineCallbacks
    def onClose(self, wasClean, code, reason):
        print('TeraWebSocketServerDeviceProtocol - onClose', self, wasClean, code, reason)
        if self.device:
            # Advertise that device leaved
            tera_message = self.create_tera_message(
                create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            device_disconnected = messages.DeviceEvent()
            device_disconnected.device_uuid = str(self.device.device_uuid)
            device_disconnected.device_name = self.device.device_name
            device_disconnected.type = messages.DeviceEvent.DEVICE_DISCONNECTED

            # Need to use Any container
            any_message = messages.Any()
            any_message.Pack(device_disconnected)
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

            # log information
            self.logger.log_info(self, "Device websocket disconnected",
                                 self.device.device_name, self.device.device_uuid)

            print(ret1, ret2, ret3)

        # Unsubscribe to messages
        # ret = yield self.unsubscribe_pattern_with_callback(self.answer_topic(), self.redis_tera_message_received)
        # print(ret)

    def answer_topic(self):
        if self.device:
            return 'websocket.device.' + self.device.device_uuid
        super().answer_topic()

    def event_topic(self):
        if self.device:
            return 'websocket.device.' + self.device.device_uuid + '.events'
        super().event_topic()

