from services.VideoDispatch.ConfigManager import ConfigManager
from messages.python.CreateSession_pb2 import CreateSession
from modules.BaseModule import BaseModule, ModuleNames

import os
import subprocess
import threading


class ActiveSession:
    def test(self):
        pass


class WebRTCModule(BaseModule):

    def __init__(self, config: ConfigManager):
        BaseModule.__init__(self, "VideoDispatchService.WebRTCModule", config)
        self.processList = []

    def __del__(self):
        # self.unsubscribe_pattern_with_callback("webrtc.*", self.webrtc_message_callback_deprecated)
        pass

    def setup_module_pubsub(self):
        # Additional subscribe
        # TODO change those messages to use complete protobuf messaging system
        # self.subscribe_pattern_with_callback("webrtc.*", self.webrtc_message_callback_deprecated)
        pass

    def setup_rpc_interface(self):
        self.rpc_api['create_session'] = {'args': ['str:room_name'],
                                          'returns': 'dict',
                                          'callback': self.create_webrtc_session}

    def create_webrtc_session(self, room_name, *args, **kwargs):
        print('Should create WebRTC session with name:', room_name)

        # For now just launch test
        port = 8080
        key = room_name

        url = 'https://' + self.config.webrtc_config['hostname'] + ':' + str(port) + '/teraplus?key=' + key

        if self.launch_node(port=port, key=key):
            # Return empty dict
            return {'url': url}
        else:
            return {'error': 'Not launched.'}

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('WebRTCModule - Received message ', pattern, channel, message)
        pass

    def launch_node(self, port, key):
        executable_args = [self.config.webrtc_config['executable'],
                           self.config.webrtc_config['command'],
                           str(port),
                           str(key)]

        # stdout=os.subprocess.PIPE, stderr=os.subprocess.PIPE)
        try:
            process = subprocess.Popen(executable_args,
                                     cwd=os.path.realpath(self.config.webrtc_config['working_directory']),
                                     shell=True)

            # One more process
            self.processList.append({'process': process, 'port': port, 'key': key})

            print('started process', process)
            return True
        except OSError as e:
            print('error!', e)

        return False


if __name__ == '__main__':
    # Mini test
    from services.VideoDispatch.Globals import config_man
    from twisted.internet import reactor, task, threads
    import services.VideoDispatch.Globals as Globals
    from modules.RedisVars import RedisVars
    from libtera.redis.RedisClient import RedisClient
    from twisted.python import log
    import sys
    from twisted.internet import defer

    # Used for redis events...
    log.startLogging(sys.stdout)

    # Load configuration
    config_man.load_config('VideoDispatchService.ini')

    # Init global variables
    Globals.redis_client = RedisClient(config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)

    # Create module
    module = WebRTCModule(config_man)

    def result_callback(result):
        print(result)


    def rpc_call():

        print('current thread', threading.current_thread())
        # Create session message
        from messages.python.CreateSession_pb2 import CreateSession
        from messages.python.RPCMessage_pb2 import RPCMessage
        from libtera.redis.RedisClient import RedisClient
        from libtera.redis.RedisRPCClient import RedisRPCClient
        from datetime import datetime

        print('Calling RPC')
        # Using RPC API
        rpc = RedisRPCClient(config_man.redis_config)

        result = rpc.call('VideoDispatchService.WebRTCModule', 'create_session', 'test')

        print(result)
        return result
        # ret.addCallback(subscribed_callback)

    # Deferred to call function in 5 secs.
    d = threads.deferToThread(rpc_call)
    d.addCallback(result_callback)
    reactor.run()
