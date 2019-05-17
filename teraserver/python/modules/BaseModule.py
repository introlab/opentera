from libtera.redis.RedisClient import RedisClient
from libtera.ConfigManager import ConfigManager
from enum import Enum, unique


@unique
class ModuleNames(Enum):
    FLASK_MODULE_NAME = str("FlaskModule")
    WEBRTC_MODULE_NAME = str("WebRTCModule")
    TWISTED_MODULE_NAME = str("TwistedModule")
    LOGIN_MODULE_NAME = str("LoginModule")
    USER_MANAGER_MODULE_NAME = str("UserManagerModule")


def create_module_topic_from_name(name: ModuleNames):
    return 'module.' + name.value + '.messages'


class BaseModule(RedisClient):
    """
        BaseModule will handle basic registration of topics and events.

    """
    def __init__(self, module_name, config: ConfigManager):

        # Set module name
        # TODO verify module name
        self.module_name = module_name

        # Store config
        self.config = config

        # Init redis with configuration
        RedisClient.__init__(self, config=config.redis_config)

    def get_name(self):
        return self.module_name

    def redisConnectionMade(self):
        print('BaseModule.connectionMade')

        # Build standard interface
        self.build_interface()

        # Setup pubsub for module, needs to be overridden
        self.setup_module_pubsub()

    def setup_module_pubsub(self):
        pass

    def build_interface(self):
        self.subscribe_pattern_with_callback("module." + self.module_name + ".messages", self.notify_module_messages)

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('BaseModule - Received message ', pattern, channel, message)
        pass


