from libtera.redis.RedisClient import RedisClient
from libtera.ConfigManager import ConfigManager
from messages.python.CreateSession_pb2 import CreateSession
import os
import subprocess


# Will use twisted Async Redis client
class WebRTCModule(RedisClient):

    def __init__(self, config: ConfigManager):
        self.config = config
        self.processList = []
        RedisClient.__init__(self, config=self.config.redis_config)
        # self.launch_node()

    def redisConnectionMade(self):
        print('WebRTCModule.redisConnectionMade')
        self.subscribe('webrtc.*')

    def create_session(self, message: CreateSession):

        print('create_session', message)

        # For now just launch test
        port = 8080
        key = "test"

        url = 'https://'+self.config.webrtc_config['hostname'] + ':' + str(port) + '?key=' + key
        self.launch_node(port=port, key=key)
        self.publish(message.reply_to, url)

    def redisMessageReceived(self, pattern, channel, message):
        print('WebRTCModule message received', pattern, channel, message)
        parts = channel.split('.')
        if len(parts) == 2 and 'webrtc' in parts[0]:
            # Verify command
            if 'create_session' in parts[1]:
                len_message = len(message)
                protobuf_message = CreateSession()
                protobuf_message.ParseFromString(message.encode('utf-8'))
                print('got protobuf_message: ', protobuf_message)

                """
                got protobuf_message:  source: "UserManagerModule"
                2019-04-02 15:27:40-0400 [-] command: "create_session"
                2019-04-02 15:27:40-0400 [-] reply_to: "server.f9ee231b-8fce-43c2-8075-a9c6f90368fe.create_session"
                """
                self.create_session(protobuf_message)
                # self.publish(protobuf_message.reply_to, 'should send back webrtc server info')

    def launch_node(self, port=8080, key="test"):
        command = [self.config.webrtc_config['executable'],
                   self.config.webrtc_config['script'], str(port), str(key)]

        # stdout=os.subprocess.PIPE, stderr=os.subprocess.PIPE)
        process = subprocess.Popen(command, cwd=os.path.realpath(self.config.webrtc_config['working_directory']))

        # One more process
        self.processList.append({'process': process, 'port': port, 'key': key})

        print('started process', process)

