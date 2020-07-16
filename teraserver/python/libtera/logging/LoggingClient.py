from redis import Redis
import messages.python as messages
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
    """

    def __init__(self, config):
        # Setup connection with redis
        self.redis = Redis(host=config['hostname'], port=config['port'], password=config['password'], db=config['db'])

    def log_trace(self, sender: str, *args):
        self._send_tera_event_message(self._create_log_event(messages.LogEvent.LOGLEVEL_TRACE, sender, *args))

    def log_debug(self, sender: str, *args):
        self._send_tera_event_message(self._create_log_event(messages.LogEvent.LOGLEVEL_DEBUG, sender, *args))

    def log_info(self, sender: str, *args):
        self._send_tera_event_message(self._create_log_event(messages.LogEvent.LOGLEVEL_INFO, sender, *args))

    def log_warning(self, sender: str, *args):
        self._send_tera_event_message(self._create_log_event(messages.LogEvent.LOGLEVEL_WARNING, sender, *args))

    def log_critical(self, sender: str, *args):
        self._send_tera_event_message(self._create_log_event(messages.LogEvent.LOGLEVEL_CRITICAL, sender, *args))

    def log_error(self, sender: str, *args):
        self._send_tera_event_message(self._create_log_event(messages.LogEvent.LOGLEVEL_ERROR, sender, *args))

    def log_fatal(self, sender: str, *args):
        self._send_tera_event_message(self._create_log_event(messages.LogEvent.LOGLEVEL_FATAL, sender, *args))

    def log_debug(self, sender: str, *args):
        self._send_tera_event_message(self._create_log_event(messages.LogEvent.LOGLEVEL_DEBUG, sender, *args))

    def _create_log_event(self, level, sender, *args):
        log_event = messages.LogEvent()
        log_event.level = level
        log_event.timestamp = datetime.datetime.now().timestamp()
        log_event.sender = sender
        log_event.message = str(args)
        return log_event

    def _send_tera_event_message(self, log_event: messages.LogEvent):
        event_message = messages.TeraEvent()
        event_message.header.version = 1
        # Duplicated time, useful?
        event_message.header.time = log_event.timestamp
        level_string = 'unknown'

        # Convert level to string
        if log_event.level == messages.LogEvent.LOGLEVEL_TRACE:
            level_string = 'trace'
        elif log_event.level == messages.LogEvent.LOGLEVEL_DEBUG:
            level_string = 'debug'
        elif log_event.level == messages.LogEvent.LOGLEVEL_INFO:
            level_string = 'info'
        elif log_event.level == messages.LogEvent.LOGLEVEL_WARNING:
            level_string = 'warning'
        elif log_event.level == messages.LogEvent.LOGLEVEL_CRITICAL:
            level_string = 'critical'
        elif log_event.level == messages.LogEvent.LOGLEVEL_ERROR:
            level_string = 'error'
        elif log_event.level == messages.LogEvent.LOGLEVEL_FATAL:
            level_string = 'fatal'

        event_message.header.topic = 'log.' + level_string

        # Add log event
        any_message = messages.Any()
        any_message.Pack(log_event)
        event_message.events.extend([any_message])

        # Publish message
        self.redis.publish(event_message.header.topic, event_message.SerializeToString())

        return event_message


if __name__ == '__main__':
    from libtera.ConfigManager import ConfigManager
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
