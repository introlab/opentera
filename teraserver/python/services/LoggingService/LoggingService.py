from services.LoggingService.FlaskModule import flask_app
import services.LoggingService.Globals as Globals
from opentera.redis.RedisClient import RedisClient
from services.LoggingService.ConfigManager import ConfigManager
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
from services.LoggingService.FlaskModule import FlaskModule


class LoggingService(ServiceOpenTera):
    def __init__(self, config_man: ConfigManager, this_service_info):
        ServiceOpenTera.__init__(self, config_man, this_service_info)

        # Create REST backend
        self.flaskModule = FlaskModule(Globals.config_man)

        # Create twisted service
        self.flaskModuleService = self.flaskModule.create_service()

        # self.application = service.Application(self.config['name'])

        # TODO update log level according to configuration
        # TODO will log everything for now
        self.loglevel = messages.LogEvent.LOGLEVEL_TRACE

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
        ret1 = yield self.subscribe_pattern_with_callback('log.*', self.log_event_received)
        print(ret1)

        log_levels = ['log.trace', 'log.debug', 'log.info', 'log.warning', 'log.critical', 'log.error', 'log.fatal']

        for level in log_levels:
            loop = task.LoopingCall(self.read_queues, level)

            # Start looping every 1 second.
            d = loop.start(1.0)

            # Add callbacks for stop and failure.
            d.addCallback(self.cbLoopDone)
            d.addErrback(self.ebLoopFailed)

    def log_event_received(self, pattern, channel, message):
        # print('LoggingService - user_manager_event_received', pattern, channel, message)
        try:
            tera_event = messages.TeraEvent()
            if isinstance(message, str):
                ret = tera_event.ParseFromString(message.encode('utf-8'))
            elif isinstance(message, bytes):
                ret = tera_event.ParseFromString(message)

            log_event = messages.LogEvent()

            # Look for UserEvent, ParticipantEvent, DeviceEvent
            for any_msg in tera_event.events:
                if any_msg.Unpack(log_event):
                    # Check current log level, store db if lower than current log level
                    if log_event.level <= self.loglevel:
                        Globals.db_man.store_log_event(log_event)
                    else:
                        print(log_event)

        except DecodeError as d:
            print('LoggingService - DecodeError ', pattern, channel, message, d)
        except ParseError as e:
            print('LoggingService - Failure in redisMessageReceived', e)

    def setup_rpc_interface(self):
        # TODO Update rpc interface
        self.rpc_api['set_loglevel'] = {'args': ['str:loglevel'],
                                          'returns': 'dict',
                                          'callback': self.set_loglevel}

    def set_loglevel(self, loglevel):
        pass


if __name__ == '__main__':

    # Very first thing, log to stdout
    log.startLogging(sys.stdout)

    # Load configuration
    if not Globals.config_man.load_config('LoggingService.json'):
        print('Invalid config')
        exit(1)

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

    try:
        Globals.db_man.open(POSTGRES, Globals.config_man.service_config['debug_mode'])
    except OperationalError as e:
        print("Unable to connect to database - please check settings in config file!",e)
        quit()

    with flask_app.app_context():
        Globals.db_man.create_defaults(Globals.config_man)

    # Create the Service
    service = LoggingService(Globals.config_man, service_info)

    # Start App / reactor events
    reactor.run()
