from modules.BaseModule import BaseModule, ModuleNames
from .ConfigManager import ConfigManager


class OnlineUsersModule(BaseModule):

    def __init__(self,  config: ConfigManager):
        BaseModule.__init__(self, "VideoDispatchService.OnlineUsersModule", config)

    def setup_module_pubsub(self):
        # Additional subscribe
        self.subscribe_pattern_with_callback('module.TeraServer.UserManagerModule.messages.events',
                                             self.notify_user_manager_event)

    def notify_user_manager_event(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('VideoDispatchService.OnlineUsersModule - notify_user_manager_event', pattern, channel, message)
        pass

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('VideoDispatchService.OnlineUsersModule - Received message ', pattern, channel, message)
        pass

