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

    def setup_rpc_interface(self):
        self.rpc_api['online_users'] = {'args': [], 'returns': 'list', 'callback': self.online_users_rpc_callback}

    def online_users_rpc_callback(self, *args, **kwargs):
        print('online_users_rpc_callback', args, kwargs)
        online_users = str(self.registry.online_users())
        return online_users

    def setup_module_pubsub(self):
        pass

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





