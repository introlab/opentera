from opentera.redis.RedisClient import RedisClient
from enum import Enum, unique
import opentera.messages.python as messages
from opentera.logging.LoggingClient import LoggingClient

import json
import datetime


@unique
class ModuleNames(Enum):
    FLASK_MODULE_NAME = str("TeraServer.FlaskModule")
    TWISTED_MODULE_NAME = str("TeraServer.TwistedModule")
    LOGIN_MODULE_NAME = str("TeraServer.LoginModule")
    USER_MANAGER_MODULE_NAME = str("TeraServer.UserManagerModule")
    DATABASE_MODULE_NAME = str("TeraServer.DatabaseModule")
    SERVICE_LAUNCHER_NAME = str("TeraServer.ServiceLauncherModule")


def create_module_message_topic_from_name(name: ModuleNames):
    return 'module.' + name.value + '.messages'


def create_module_event_topic_from_name(name: ModuleNames, subtopic=None):
    if subtopic:
        return 'module.' + name.value + '.events.' + str(subtopic)
    else:
        return 'module.' + name.value + '.events'


class BaseModule(RedisClient):
    """
        BaseModule will handle basic registration of topics and events.

    """
    def __init__(self, module_name, config):

        # Set module name
        # TODO verify module name to be unique
        self.module_name = module_name

        # Store config
        self.config = config

        # Store RPC API
        self.rpc_api = dict()

        # Logger
        self.logger = LoggingClient(config.redis_config, 'LoggingClient_' + self.__class__.__name__)

        # Init redis with configuration
        RedisClient.__init__(self, config=config.redis_config)

    def get_name(self):
        return self.module_name

    def event_topic_name(self):
        return 'module.' + self.module_name + '.events'

    def send_event_message(self, event, topic: str):
        message = self.create_event_message(topic)
        any_message = messages.Any()
        any_message.Pack(event)
        message.events.extend([any_message])
        self.publish(message.header.topic, message.SerializeToString())

    def send_module_message(self, message: messages.TeraModuleMessage):
        self.publish(message.head.dest, message.SerializeToString())

    def redisConnectionMade(self):
        print('*************************** BaseModule.connectionMade', self.module_name)

        # Build RPC interface
        self.setup_rpc_interface()

        # Build standard interface
        self.build_interface()

        # Setup pubsub for module, needs to be overridden
        self.setup_module_pubsub()

    def setup_module_pubsub(self):
        pass

    def build_interface(self):
        # TeraModuleMessage Interface
        def messages_subscribed_callback(*args):
            print('messages_subscribed_callback for ', self.module_name)

        ret1 = self.subscribe_pattern_with_callback('module.' + self.module_name + '.messages', self.notify_module_messages)
        ret1.addCallback(messages_subscribed_callback)

        # RPC messages
        def rpc_subscribed_callback(*args):
            print('rpc_subscribed_callback for ', self.module_name)
        ret2 = self.subscribe_pattern_with_callback('module.' + self.module_name + '.rpc', self.notify_module_rpc)
        ret2.addCallback(rpc_subscribed_callback)

    def setup_rpc_interface(self):
        pass

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('BaseModule - Received message', self, pattern, channel, message)
        pass

    def notify_module_rpc(self, pattern, channel, message):
        # print('BaseModule - Received rpc', self, pattern, channel, message, ' thread:', threading.current_thread())

        try:
            # Look for a RPCMessage
            rpc_message = messages.RPCMessage()
            rpc_message.ParseFromString(message)

            if self.rpc_api.__contains__(rpc_message.method):

                # RPC method found, call it with the args
                args = list()
                kwargs = dict()

                # TODO type checking with declared rpc interface ?
                for value in rpc_message.args:
                    # Append the oneof value to args
                    args.append(getattr(value, value.WhichOneof('arg_value')))

                # Call callback function
                ret_value = self.rpc_api[rpc_message.method]['callback'](*args, **kwargs)

                # More than we need?
                my_dict = {'method': rpc_message.method,
                           'id': rpc_message.id,
                           'pattern': pattern,
                           'status': 'OK',
                           'return_value': ret_value}

                json_data = json.dumps(my_dict)

                # Return result (a json string)
                self.publish(rpc_message.reply_to, json_data)

        except:
            import sys
            print('Error calling rpc method', message, sys.exc_info())
            my_dict = {'method': rpc_message.method,
                       'id': rpc_message.id,
                       'pattern': pattern,
                       'status': 'Error',
                       'return_value': None}

            json_data = json.dumps(my_dict)

            # Return result (a json string)
            self.publish(rpc_message.reply_to, json_data)

    def create_tera_message(self, dest='', seq=0):
        tera_message = messages.TeraModuleMessage()
        tera_message.head.version = 1
        tera_message.head.time = datetime.datetime.now().timestamp()
        tera_message.head.seq = seq
        tera_message.head.source = 'module.' + self.module_name
        tera_message.head.dest = dest
        return tera_message

    def create_event_message(self, topic):
        event_message = messages.TeraEvent()
        event_message.header.version = 1
        event_message.header.time = datetime.datetime.now().timestamp()
        event_message.header.topic = topic
        return event_message

    def create_module_message(self, src, dest):
        """
            message Header {
            uint32 version = 1;
            double time = 2;
            uint32 seq = 3;
            string source = 4;
            string dest = 5;
        }
        Header head = 1;
        repeated google.protobuf.Any data = 2;
        """

        module_message = messages.TeraModuleMessage()
        module_message.head.version = 1
        module_message.head.time = datetime.datetime.now().timestamp()
        module_message.head.seq = 0
        module_message.head.source = src
        module_message.head.dest = dest
        return module_message

    def source_name(self):
        return "module." + self.module_name + ".messages"

    def _send_disconnect_module_message(self, uuid: str):
        module_message = self.create_module_message(
            src='module.' + self.module_name + '.messages',
            dest=create_module_event_topic_from_name(ModuleNames.TWISTED_MODULE_NAME, uuid)
        )
        server_command = messages.ServerCommand()
        server_command.type = messages.ServerCommand.CMD_CLIENT_DISCONNECT
        command_message = messages.Any()
        command_message.Pack(server_command)
        module_message.data.extend([command_message])
        self.send_module_message(module_message)

    def send_user_disconnect_module_message(self, user_uuid: str):
        self._send_disconnect_module_message(user_uuid)

    def send_participant_disconnect_module_message(self, participant_uuid: str):
        self._send_disconnect_module_message(participant_uuid)

    def send_device_disconnect_module_message(self, device_uuid: str):
        self._send_disconnect_module_message(device_uuid)
