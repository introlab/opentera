import redis
from opentera.messages.python.RPCMessage_pb2 import RPCMessage, Value
from datetime import datetime
import json
import uuid
from opentera.redis.RedisVars import RedisVars


class RedisRPCClient:
    def __init__(self, config: dict, timeout=10):
        self.config = config
        self.timeout = timeout
        # Create a unique random pattern
        self.pattern = 'RedisRPCClient.' + str(uuid.uuid4())
        self.msg_id = 0
        self.client = redis.Redis(host=self.config['hostname'],
                                  port=self.config['port'],
                                  db=self.config['db'],
                                  username=self.config['username'],
                                  password=self.config['password'],
                                  client_name=self.pattern)

    # def __del__(self):
    #     print('****- Deleting RedisRPCClient')

    def _internal_rpc_call(self, topic: str, function_name: str, *args):
        # Pub/Sub client
        p = self.client.pubsub()

        message = RPCMessage()
        message.method = function_name
        message.timestamp = datetime.now().timestamp()
        message.id = self.msg_id
        self.msg_id = self.msg_id + 1
        message.reply_to = self.pattern

        # Iterate through args
        rpc_args = []
        for arg in args:
            if isinstance(arg, bool):
                val = Value()
                val.bool_value = arg
                rpc_args.append(val)
            elif isinstance(arg, float):
                val = Value()
                val.double_value = arg
                rpc_args.append(val)
            elif isinstance(arg, int):
                val = Value()
                val.int_value = arg
                rpc_args.append(val)
            elif isinstance(arg, str):
                val = Value()
                val.string_value = arg
                rpc_args.append(val)
            elif isinstance(arg, bytes):
                val = Value()
                val.bytes_value = arg
                rpc_args.append(val)
            else:
                print('Invalid arg:', arg)

        # Set args
        message.args.extend(rpc_args)

        # Will answer on the replay_to field
        p.subscribe(message.reply_to)
        # First message is for subscribe result
        message1 = p.get_message(timeout=self.timeout)

        # Publish request
        self.client.publish(topic, message.SerializeToString())

        # Second message is data received
        message2 = p.get_message(timeout=self.timeout)

        # Unsubscribe to message
        # p.unsubscribe(message.reply_to)
        # Closing (will automatically unsubscribe)
        p.close()

        if message2:
            result = json.loads(message2['data'])
            return result['return_value']

        return None

    def call(self, module_name: str, function_name: str, *args):
        return self._internal_rpc_call('module.' + module_name + '.rpc', function_name, *args)

    def call_service(self, service_key: str, function_name: str, *args):
        return self._internal_rpc_call(RedisVars.build_service_rpc_topic(service_key), function_name, *args)

