from libtera.ConfigManager import ConfigManager
from messages.python.TeraMessage_pb2 import TeraMessage
from messages.python.CreateSession_pb2 import CreateSession
from messages.python.UserConnected_pb2 import UserConnected
from messages.python.UserDisconnected_pb2 import UserDisconnected
from modules.BaseModule import BaseModule, ModuleNames, create_module_topic_from_name
from google.protobuf.any_pb2 import Any


class OnlineUserRegistry:
    def __init__(self):
        self.user_list = list()

    def user_online(self, uuid):
        print('user_online: ', uuid)
        if not self.user_list.__contains__(uuid):
            self.user_list.append(uuid)

    def user_offline(self, uuid):
        print('user_offline', uuid)
        if self.user_list.__contains__(uuid):
            self.user_list.remove(uuid)

    def online_users(self):
        return self.user_list


class UserManagerModule(BaseModule):

    def __init__(self, config: ConfigManager):
        BaseModule.__init__(self, ModuleNames.USER_MANAGER_MODULE_NAME.value, config)

        # Create user registry
        self.registry = OnlineUserRegistry()

    def __del__(self):
        pass
        # self.unsubscribe_pattern_with_callback("websocket.*", self.notify_websocket_messages_deprecated)
        # self.unsubscribe_pattern_with_callback("api.*", self.notify_api_messages_deprecated)

    def setup_module_pubsub(self):
        pass
        # Additional subscribe (old stuff to be removed)
        # self.subscribe_pattern_with_callback("websocket.*", self.notify_websocket_messages_deprecated)
        # self.subscribe_pattern_with_callback("api.*", self.notify_api_messages_deprecated)

    def notify_websocket_messages_deprecated(self, pattern, channel, message):
        """
        Deprecated, should be replaced with protobuf messages
        """
        parts = channel.split('.')
        if 'websocket' in parts[0]:
            self.handle_websocket_messages(parts[1], message)

    def notify_api_messages_deprecated(self, pattern, channel, message):
        """
            Deprecated, should be replaced with protobuf messages
        """
        parts = channel.split('.')
        if 'api' in parts[0]:
            self.handle_api_messages(parts[1], parts[2], message)

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('UserManagerModule - Received message ', pattern, channel, message)

        tera_message = TeraMessage()
        tera_message.ParseFromString(message)
        # tera_message.ParseFromString(message.encode('utf-8'))

        # We have a repeated Any field look for message type
        for any_msg in tera_message.data:
            # Test for UserConnected
            user_connected = UserConnected()
            if any_msg.Unpack(user_connected):
                self.handle_user_connected(tera_message.head, user_connected)

            # Test for UserDisconnected
            user_disconnected = UserDisconnected()
            if any_msg.Unpack(user_disconnected):
                self.handle_user_disconnected(tera_message.head, user_disconnected)

    def handle_user_connected(self, header, user_connected: UserConnected):
        self.registry.user_online(user_connected.user_uuid)

        for user_uuid in self.registry.online_users():
            # TODO Check for permissions...
            # Send to everyone?
            tera_message = TeraMessage()
            tera_message.head.source = create_module_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME)
            tera_message.head.dest = 'websocket.user.' + user_uuid

            any_message = Any()
            any_message.Pack(user_connected)
            tera_message.data.extend([any_message])

            self.publish(tera_message.head.dest, tera_message.SerializeToString())

    def handle_user_disconnected(self, header, user_disconnected: UserDisconnected):
        self.registry.user_offline(user_disconnected.user_uuid)

    def handle_api_messages(self, module, uuid, message):
        print('handle_api_messages', module, uuid, message)
        if message == b'list' or message == 'list':
            online_users = str(self.registry.online_users())
            # Answer
            print('answering', 'server.' + module + '.' + str(uuid) + '.answer', online_users)
            self.publish('server.' + module + '.' + str(uuid) + '.answer', online_users)
            return True

    def handle_websocket_messages(self, uuid, message):
        print('handle_websocket_messages', uuid, message)
        if message == b'list' or message == 'list':
            online_users = str(self.registry.online_users())
            # Answer
            print('answering', 'server.' + str(uuid) + '.answer', online_users)
            self.publish('server.' + str(uuid) + '.answer', online_users)
            return True
        if message == b'session' or message == 'session':
            # Create message
            protobuf_message = CreateSession(source='UserManagerModule',
                                             command='create_session',
                                             reply_to='server.' + uuid + '.create_session')

            # Send message to WebRTCModule
            self.publish('webrtc.' + 'create_session', protobuf_message.SerializeToString())

        print('Error unhandled message ', uuid, message)
        return False


