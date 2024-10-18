from services.EmailService.FlaskModule import flask_app
import services.EmailService.Globals as Globals
from opentera.redis.RedisClient import RedisClient
from services.EmailService.ConfigManager import ConfigManager
from opentera.services.ServiceAccessManager import ServiceAccessManager
from opentera.redis.RedisVars import RedisVars
from google.protobuf.json_format import ParseError
from google.protobuf.message import DecodeError

# Twisted
from twisted.internet import reactor, defer, task
from twisted.python import log
import opentera.messages.python as messages
import sys

from opentera.services.ServiceOpenTera import ServiceOpenTera
from sqlalchemy.exc import OperationalError
from services.EmailService.FlaskModule import FlaskModule


class EmailService(ServiceOpenTera):
    def __init__(self, config_man: ConfigManager, this_service_info):
        ServiceOpenTera.__init__(self, config_man, this_service_info)

        # Create REST backend
        self.flaskModule = FlaskModule(Globals.config_man)

        # Create twisted service
        self.flaskModuleService = self.flaskModule.create_service()

    def notify_service_messages(self, pattern, channel, message):
        pass

    def read_queues(self, queue_name: str):
        # print('read_queues', queue_name)
        # Reading queue
        while self.redis.llen(queue_name) > 0:
            message = self.redis.lpop(queue_name)
            self.log_event_received(queue_name, queue_name, message)

    def cbLoopDone(self, result):
        """
        Called when loop was stopped with success.
        """
        print('cbLoopDone', result)

    def ebLoopFailed(self, failure):
        """
        Called when loop execution failed.
        """
        print('ebLoopFailed', failure)

    @defer.inlineCallbacks
    def register_to_events(self):
        # Need to register to events produced by UserManagerModule
        yield None
        # ret1 = yield self.subscribe_pattern_with_callback('log.*', self.log_event_received)
        # print(ret1)
        #
        # log_levels = ['log.trace', 'log.debug', 'log.info', 'log.warning', 'log.critical', 'log.error', 'log.fatal']
        #
        # for level in log_levels:
        #     loop = task.LoopingCall(self.read_queues, level)
        #
        #     # Start looping every 1 second.
        #     d = loop.start(1.0)
        #
        #     # Add callbacks for stop and failure.
        #     d.addCallback(self.cbLoopDone)
        #     d.addErrback(self.ebLoopFailed)


    def setup_rpc_interface(self):
        # TODO Update rpc interface
        pass
        # self.rpc_api['set_loglevel'] = {'args': ['str:loglevel'],
        #                                   'returns': 'dict',
        #                                   'callback': self.set_loglevel}


if __name__ == '__main__':

    # Load configuration
    if not Globals.config_man.load_config('EmailService.json'):
        print('Invalid config')
        exit(1)

    import argparse

    parser = argparse.ArgumentParser(description='Email Service')
    parser.add_argument('--enable_tests', help='Test mode for service.', default=False)
    args = parser.parse_args()

    # Global redis client
    Globals.redis_client = RedisClient(Globals.config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
    Globals.api_device_static_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceStaticTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)
    Globals.api_participant_static_token_key = \
        Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantStaticTokenAPIKey)

    # Update Service Access information
    ServiceAccessManager.api_user_token_key = Globals.api_user_token_key
    ServiceAccessManager.api_participant_token_key = Globals.api_participant_token_key
    ServiceAccessManager.api_participant_static_token_key = Globals.api_participant_static_token_key
    ServiceAccessManager.api_device_token_key = Globals.api_device_token_key
    ServiceAccessManager.api_device_static_token_key = Globals.api_device_static_token_key
    ServiceAccessManager.config_man = Globals.config_man

    # Get service UUID
    service_info = Globals.redis_client.redisGet(RedisVars.RedisVar_ServicePrefixKey +
                                                 Globals.config_man.service_config['name'])
    import sys
    if service_info is None:
        sys.stderr.write('Error: Unable to get service info from OpenTera Server - is the server running and config '
                         'correctly set in this service?')
        exit(1)
    import json
    service_info = json.loads(service_info)
    if 'service_uuid' not in service_info:
        sys.stderr.write('OpenTera Server didn\'t return a valid service UUID - aborting.')
        exit(1)

    # Update service uuid
    Globals.config_man.service_config['ServiceUUID'] = service_info['service_uuid']

    # Update port, hostname, endpoint
    Globals.config_man.service_config['port'] = service_info['service_port']
    Globals.config_man.service_config['hostname'] = service_info['service_hostname']

    # DATABASE CONFIG AND OPENING
    #############################
    POSTGRES = {
        'user': Globals.config_man.db_config['username'],
        'pw': Globals.config_man.db_config['password'],
        'db': Globals.config_man.db_config['name'],
        'host': Globals.config_man.db_config['url'],
        'port': Globals.config_man.db_config['port']
    }

    Globals.db_man.test = args.enable_tests

    if not args.enable_tests:
        try:
            Globals.db_man.open(POSTGRES, Globals.config_man.service_config['debug_mode'])
        except OperationalError as e:
            print("Unable to connect to database - please check settings in config file!", e)
            quit()

        with flask_app.app_context():
            Globals.db_man.create_defaults(Globals.config_man)

    # In test mode, db manager will not save anything into a database

    # Create the Service
    Globals.service = EmailService(Globals.config_man, service_info)

    # Start App / reactor events
    reactor.run()
