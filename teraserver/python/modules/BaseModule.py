from libtera.redis.RedisClient import RedisClient
from libtera.ConfigManager import ConfigManager
from enum import Enum, unique
from messages.python.TeraMessage_pb2 import TeraMessage
from messages.python.RPCMessage_pb2 import RPCMessage

import json
import datetime


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
        # TODO verify module name to be unique
        self.module_name = module_name

        # Store config
        self.config = config

        # Store RPC API
        self.rpc_api = dict()

        # Init redis with configuration
        RedisClient.__init__(self, config=config.redis_config)

    def get_name(self):
        return self.module_name

    def redisConnectionMade(self):
        print('BaseModule.connectionMade')

        # Build RPC interface
        self.setup_rpc_interface()

        # Build standard interface
        self.build_interface()

        # Setup pubsub for module, needs to be overridden
        self.setup_module_pubsub()

    def setup_module_pubsub(self):
        pass

    def build_interface(self):
        # TeraMessage Interface
        self.subscribe_pattern_with_callback("module." + self.module_name + ".messages", self.notify_module_messages)

        # RPC messages
        self.subscribe_pattern_with_callback("module." + self.module_name + ".rpc", self.notify_module_rpc)

    def setup_rpc_interface(self):
        pass

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('BaseModule - Received message', self, pattern, channel, message)
        pass

    def notify_module_rpc(self, pattern, channel, message):
        print('BaseModule - Received rpc', self, pattern, channel, message)

        try:
            # Look for a RPCMessage
            rpc_message = RPCMessage()
            rpc_message.ParseFromString(message)

            if self.rpc_api.__contains__(rpc_message.method):

                # RPC method found, call it with the args
                args = list()
                kwargs = dict()

                # TODO type checking with declared rpc interface
                for value in rpc_message.args:
                    pass

                # Call callback function
                value = self.rpc_api[rpc_message.method]['callback'](*args, **kwargs)

                # More than we need?
                my_dict = {'method': rpc_message.method,
                           'id': rpc_message.id,
                           'pattern': pattern,
                           'status': 'OK',
                           'return_value': value}

                json_data = json.dumps(my_dict)

                # Return result (a json string)
                self.publish(rpc_message.reply_to, json_data)

        except:
            print('Error calling rpc method', message)
            my_dict = {'method': rpc_message.method,
                       'id': rpc_message.id,
                       'pattern': pattern,
                       'status': 'Error',
                       'return_value': None}

            json_data = json.dumps(my_dict)

            # Return result (a json string)
            self.publish(rpc_message.reply_to, json_data)

    def create_tera_message(self, dest='', seq=0):

        tera_message = TeraMessage()
        tera_message.head.version = 1
        tera_message.head.time = datetime.datetime.now().timestamp()
        tera_message.head.seq = seq
        tera_message.head.source = 'module.' + self.module_name
        tera_message.head.dest = dest
        return tera_message

    def source_name(self):
        return "module." + self.module_name + ".messages"
