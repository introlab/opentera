from redis import Redis
import opentera.messages.python as messages
import datetime


class LoggingClient:
    """
    enum LogLevel
    {
        LOGLEVEL_UNKNOWN = 0;
        LOGLEVEL_TRACE = 1;
        LOGLEVEL_DEBUG = 2;
        LOGLEVEL_INFO = 3;
        LOGLEVEL_WARNING = 4;
        LOGLEVEL_CRITICAL = 5;
        LOGLEVEL_ERROR = 6;
        LOGLEVEL_FATAL = 7;

        LogLevel level = 1;
        double timestamp = 2;
        string sender = 3;
        string message = 4;
    }

    This client will send messages to queues. Logging Service is responsible of reading the queues.
    """

    def __init__(self, config, client_name='LoggingClient'):
        # Setup connection with redis
        self.client_name = client_name
        self.redis = Redis(host=config['hostname'],
                           port=config['port'],
                           username=config['username'],
                           password=config['password'],
                           db=config['db'],
                           client_name=self.client_name)

    def close(self):
        print('Closing :', self.client_name)
        self.redis.close()

    def log_trace(self, sender: str, *args):
        try:
            self._push_tera_event_message(
                LoggingClient._create_log_event(messages.LogEvent.LOGLEVEL_TRACE, sender, *args))
        # TODO Can we do better than catch base Exception here
        except Exception as e:
            print('LoggingClient.log_trace', e)

    def log_debug(self, sender: str, *args):
        try:
            self._push_tera_event_message(
                LoggingClient._create_log_event(messages.LogEvent.LOGLEVEL_DEBUG, sender, *args))
        # TODO Can we do better than catch base Exception here
        except Exception as e:
            print('LoggingClient.log_debug', e)

    def log_info(self, sender: str, *args):
        try:
            self._push_tera_event_message(
                LoggingClient._create_log_event(messages.LogEvent.LOGLEVEL_INFO, sender, *args))
        # TODO Can we do better than catch base Exception here
        except Exception as e:
            print(self.client_name + '.log_info', e)

    def log_warning(self, sender: str, *args):
        try:
            self._push_tera_event_message(
                LoggingClient._create_log_event(messages.LogEvent.LOGLEVEL_WARNING, sender, *args))
        # TODO Can we do better than catch base Exception here
        except Exception as e:
            print(self.client_name + '.log_warning', e)

    def log_critical(self, sender: str, *args):
        try:
            self._push_tera_event_message(
                LoggingClient._create_log_event(messages.LogEvent.LOGLEVEL_CRITICAL, sender, *args))
        # TODO Can we do better than catch base Exception here
        except Exception as e:
            print(self.client_name + '.log_critical', e)

    def log_error(self, sender: str, *args):
        try:
            self._push_tera_event_message(
                LoggingClient._create_log_event(messages.LogEvent.LOGLEVEL_ERROR, sender, *args))
        # TODO Can we do better than catch base Exception here
        except Exception as e:
            print(self.client_name + '.log_error', e)

    def log_fatal(self, sender: str, *args):
        try:
            self._push_tera_event_message(
                LoggingClient._create_log_event(messages.LogEvent.LOGLEVEL_FATAL, sender, *args))
        # TODO Can we do better than catch base Exception here
        except Exception as e:
            print(self.client_name + '.log_fatal', e)

    def send_login_event(self, sender: str, level: int, login_type: int, login_status: int,
                         client_name: str, client_version: str, client_ip: str, os_name: str, os_version: str,
                         user_uuid: str = '', participant_uuid: str = '', device_uuid: str = '', service_uuid: str = '',
                         server_endpoint: str = '', message: str = ''):
        # Create and fill event info
        login_event = messages.LoginEvent()
        login_event.log_header.level = level
        login_event.log_header.timestamp = datetime.datetime.now().timestamp()
        login_event.log_header.sender = str(sender)
        login_event.log_header.message = message
        login_event.login_type = login_type
        login_event.login_status = login_status
        login_event.client_name = client_name
        login_event.client_version = client_version
        login_event.client_ip = client_ip
        login_event.os_name = os_name
        login_event.os_version = os_version
        login_event.user_uuid = '' if user_uuid is None else user_uuid
        login_event.participant_uuid = '' if participant_uuid is None else participant_uuid
        login_event.device_uuid = '' if device_uuid is None else device_uuid
        login_event.service_uuid = '' if service_uuid is None else service_uuid
        login_event.server_endpoint = server_endpoint
        # Send it
        try:
            self._push_tera_login_event_message(login_event)
        except Exception as e:
            print(self.client_name + '.' + LoggingClient._loglevel_to_topic_string(login_event.log_header.level), e)

    @staticmethod
    def _create_log_event(level, sender, *args):
        log_event = messages.LogEvent()
        log_event.level = level
        log_event.timestamp = datetime.datetime.now().timestamp()
        log_event.sender = str(sender)
        log_event.message = str(args)
        return log_event

    @staticmethod
    def _loglevel_to_topic_string(level: int) -> str:
        level_string = 'unknown'

        # Convert level to string
        if level == messages.LogEvent.LOGLEVEL_TRACE:
            level_string = 'trace'
        elif level == messages.LogEvent.LOGLEVEL_DEBUG:
            level_string = 'debug'
        elif level == messages.LogEvent.LOGLEVEL_INFO:
            level_string = 'info'
        elif level == messages.LogEvent.LOGLEVEL_WARNING:
            level_string = 'warning'
        elif level == messages.LogEvent.LOGLEVEL_CRITICAL:
            level_string = 'critical'
        elif level == messages.LogEvent.LOGLEVEL_ERROR:
            level_string = 'error'
        elif level == messages.LogEvent.LOGLEVEL_FATAL:
            level_string = 'fatal'

        topic = 'log.' + level_string
        return topic

    @staticmethod
    def _create_tera_event_message(log_event: messages.LogEvent):
        event_message = messages.TeraEvent()
        event_message.header.version = 1
        # Duplicated time, useful?
        event_message.header.time = log_event.timestamp
        event_message.header.topic = LoggingClient._loglevel_to_topic_string(log_event.level)

        # Add log event
        any_message = messages.Any()
        any_message.Pack(log_event)
        event_message.events.extend([any_message])

        return event_message

    @staticmethod
    def _create_tera_event_message_from_login_event(login_event: messages.LoginEvent):
        event_message = messages.TeraEvent()
        event_message.header.version = 1
        # Duplicated time, useful?
        event_message.header.time = login_event.log_header.timestamp
        event_message.header.topic = LoggingClient._loglevel_to_topic_string(login_event.log_header.level)

        # Add log event
        any_message = messages.Any()
        any_message.Pack(login_event)
        event_message.events.extend([any_message])

        return event_message

    def _push_tera_event_message(self, log_event: messages.LogEvent):
        event_message = LoggingClient._create_tera_event_message(log_event)
        self.redis.rpush(event_message.header.topic, event_message.SerializeToString())
        return event_message

    def _push_tera_login_event_message(self, login_event: messages.LoginEvent):
        event_message = LoggingClient._create_tera_event_message_from_login_event(login_event)
        self.redis.rpush(event_message.header.topic, event_message.SerializeToString())
        return event_message


if __name__ == '__main__':
    from opentera.config.ConfigManager import ConfigManager
    import uuid

    config_man = ConfigManager()
    config_man.create_defaults()

    # Create logger
    client = LoggingClient(config_man.redis_config)
    client.log_trace('TRACE-TEST', 'hello world', 1, 2, 3, 'test', client)
    client.log_debug('DEBUG-TEST', 'hello world', 1, 2, 3, 'test', client)
    client.log_info('INFO-TEST', 'hello world', 1, 2, 3, 'test', client)
    client.log_warning('WARNING-TEST', 'hello world', 1, 2, 3, 'test', client)
    client.log_error('ERROR-TEST', 'hello world', 1, 2, 3, 'test', client)
    client.log_critical('CRITICAL-TEST', 'hello world', 1, 2, 3, 'test', client)
    client.log_fatal('FATAL-TEST', 'hello world', 1, 2, 3, 'test', client)

    client.send_login_event(sender='unknown',
                            level=messages.LogEvent.LOGLEVEL_INFO,
                            login_type=messages.LoginEvent.LOGIN_TYPE_TOKEN,
                            login_status=messages.LoginEvent.LOGIN_STATUS_SUCCESS,
                            client_name='test',
                            client_version="1.0",
                            client_ip='127.0.0.1',
                            os_name='Unknown',
                            os_version="Unknown",
                            user_uuid=str(uuid.uuid4()),
                            participant_uuid=str(uuid.uuid4()),
                            device_uuid=str(uuid.uuid4()),
                            service_uuid=str(uuid.uuid4()),
                            server_endpoint='/')

