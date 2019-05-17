from libtera.ConfigManager import ConfigManager
from messages.python.CreateSession_pb2 import CreateSession
from modules.BaseModule import BaseModule, ModuleNames


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
        BaseModule.__init__(self, ModuleNames.USER_MANAGER_MODULE_NAME, config)

        # Create user registry
        self.registry = OnlineUserRegistry()

    def __del__(self):
        self.unsubscribe_pattern_with_callback("websocket.*", self.notify_websocket_messages_deprecated)
        self.unsubscribe_pattern_with_callback("api.*", self.notify_api_messages_deprecated)

    def setup_module_pubsub(self):
        # Additional subscribe (old stuff to be removed)
        self.subscribe_pattern_with_callback("websocket.*", self.notify_websocket_messages_deprecated)
        self.subscribe_pattern_with_callback("api.*", self.notify_api_messages_deprecated)

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
        pass

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
        if message == b'connected' or message == 'connected':
            self.registry.user_online(uuid)
            return True
        if message == b'disconnected' or message == 'disconnected':
            self.registry.user_offline(uuid)
            return True
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


