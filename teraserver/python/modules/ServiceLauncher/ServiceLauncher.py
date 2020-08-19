from modules.BaseModule import BaseModule, ModuleNames
from libtera.ConfigManager import ConfigManager


class ServiceLauncherModule(BaseModule):

    def __init__(self, config: ConfigManager):
        BaseModule.__init__(self, ModuleNames.SERVICE_LAUNCHER_NAME.value, config)

    def setup_module_pubsub(self):
        # Additional subscribe here
        pass

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('ServiceLauncher - Received message ', pattern, channel, message)
        pass

    def setup_rpc_interface(self):
        pass