import jwt
import json
import time
from modules.RedisVars import RedisVars
from libtera.redis.RedisClient import RedisClient
from requests import get, post, Response
from services.shared.ServiceConfigManager import ServiceConfigManager
import messages.python as messages
from twisted.internet import defer


class ServiceOpenTera(RedisClient):

    def __init__(self, config_man: ServiceConfigManager, service_info):
        # First initialize redis
        RedisClient.__init__(self, config_man.redis_config)

        # Store service info
        self.service_info = service_info

        # Store RPC API
        self.rpc_api = dict()

        # Store config
        self.config = config_man.service_config

        # Take values from config_man
        # Values are checked when config is loaded...
        self.backend_hostname = config_man.backend_config['hostname']
        self.backend_port = config_man.backend_config['port']
        self.service_uuid = config_man.service_config['ServiceUUID']

        # TODO remove this, we already are a redis client...
        # self.redis_client

        # Create service token for future uses
        self.service_token = self.service_generate_token()

    def redisConnectionMade(self):
        print('*************************** VideoRehabService.connectionMade', self.config['name'])

        # Build RPC interface
        self.setup_rpc_interface()

        # Build standard interface
        self.build_interface()

    def setup_rpc_interface(self):
        # Should be implemented in derived class
        pass

    def notify_service_messages(self, pattern, channel, message):
        pass

    @defer.inlineCallbacks
    def build_interface(self):
        # TODO not sure of the interface using UUID or name here...
        # Will do  both!
        ret1 = yield self.subscribe_pattern_with_callback(
            RedisVars.build_service_message_topic( self.service_info['service_uuid']), self.notify_service_messages)

        ret2 = yield self.subscribe_pattern_with_callback(
            RedisVars.build_service_message_topic(self.service_info['service_key']), self.notify_service_messages)

        ret3 = yield self.subscribe_pattern_with_callback(
            RedisVars.build_service_rpc_topic(self.service_info['service_uuid']), self.notify_service_rpc)

        ret4 = yield self.subscribe_pattern_with_callback(
            RedisVars.build_service_rpc_topic(self.service_info['service_key']), self.notify_service_rpc)

        print(ret1, ret2, ret3, ret4)

    def notify_service_rpc(self, pattern, channel, message):
        import threading
        print('ServiceOpenTera - Received rpc', self, pattern, channel, message, ' thread:', threading.current_thread())

        rpc_message = messages.RPCMessage()

        try:
            # Look for a RPCMessage
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

    def service_generate_token(self):
        # Use redis key to generate token
        # Creating token with service info
        # TODO ADD MORE FIELDS?
        payload = {
            'iat': int(time.time()),
            'service_uuid': self.service_uuid
        }

        return jwt.encode(payload, self.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey),
                          algorithm='HS256').decode('utf-8')

    def post_to_opentera(self, api_url: str, json_data: dict) -> Response:
        # Synchronous call to OpenTera backend
        url = "http://" + self.backend_hostname + ':' + str(self.backend_port) + api_url
        request_headers = {'Authorization': 'OpenTera ' + self.service_token}
        return post(url=url, verify=False, headers=request_headers, json=json_data)

    def get_from_opentera(self, api_url: str, params: dict) -> Response:
        # Synchronous call to OpenTera backend
        url = "http://" + self.backend_hostname + ':' + str(self.backend_port) + api_url
        request_headers = {'Authorization': 'OpenTera ' + self.service_token}
        return get(url=url, verify=False, headers=request_headers, params=params)

