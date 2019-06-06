from libtera.ConfigManager import ConfigManager
from messages.python.TeraMessage_pb2 import TeraMessage
from messages.python.RPCMessage_pb2 import RPCMessage
from messages.python.CreateSession_pb2 import CreateSession
from messages.python.UserEvent_pb2 import UserEvent
from modules.BaseModule import BaseModule, ModuleNames, create_module_topic_from_name
from google.protobuf.any_pb2 import Any
import datetime


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

    def setup_rpc_interface(self):
        self.rpc_api['online_users'] = {'args': [], 'returns': 'list', 'callback': self.online_users_rpc_callback}

    def online_users_rpc_callback(self, *args, **kwargs):
        print('online_users_rpc_callback', args, kwargs)
        online_users = str(self.registry.online_users())
        return online_users

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
            user_event = UserEvent()
            if any_msg.Unpack(user_event):
                if user_event.type == user_event.USER_CONNECTED:
                    self.handle_user_connected(tera_message.head, user_event)
                elif user_event.type == user_event.USER_DISCONNECTED:
                    self.handle_user_disconnected(tera_message.head, user_event)

    # def notify_module_rpc(self, pattern, channel, message):
    #     print('Received rpc', self, pattern, channel, message)
    #
    #     rpc_message = RPCMessage()
    #     rpc_message.ParseFromString(message)
    #
    #     if rpc_message.method == 'online_users':
    #         online_users = str(self.registry.online_users())
    #         self.publish(rpc_message.reply_to, online_users)

    def handle_user_connected(self, header, user_event: UserEvent):
        self.registry.user_online(user_event.user_uuid)

        for user_uuid in self.registry.online_users():
            # TODO Check for permissions...
            # Send to everyone?
            tera_message = self.create_tera_message(dest='websocket.user.' + user_uuid)

            any_message = Any()
            any_message.Pack(user_event)
            tera_message.data.extend([any_message])

            self.publish(tera_message.head.dest, tera_message.SerializeToString())

    def handle_user_disconnected(self, header, user_event: UserEvent):
        self.registry.user_offline(user_event.user_uuid)

        for user_uuid in self.registry.online_users():
            # TODO Check for permissions...
            # Send to everyone?
            tera_message = self.create_tera_message(dest='websocket.user.' + user_uuid)

            any_message = Any()
            any_message.Pack(user_event)
            tera_message.data.extend([any_message])

            self.publish(tera_message.head.dest, tera_message.SerializeToString())

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


