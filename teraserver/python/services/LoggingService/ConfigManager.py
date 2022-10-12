from opentera.services.ServiceConfigManager import ServiceConfigManager, DBConfig


class LoggingConfig:
    logging_config = {}

    def __init__(self):
        pass

    def validate_logging_config(self, config: dict):
        if 'Logging' in config:
            required_fields = ['level']
            for field in required_fields:
                if field not in config['Logging']:
                    print('ERROR: Logging Config - missing field :' + field)
                    return False

            # Every field is present, update configuration
            self.logging_config = config['Logging']
            return True
        # Invalid
        return False


# Build configuration from base classes
class ConfigManager(ServiceConfigManager, LoggingConfig, DBConfig):
    def to_dict(self):
        return {
            'Service': self.service_config,
            'Backend': self.backend_config,
            'Redis': self.redis_config,
            'Logging': self.logging_config,
            'Database': self.db_config
        }

    def validate_config(self, config_json: dict):
        return super().validate_config(config_json) \
               and self.validate_logging_config(config_json) and self.validate_database_config(config_json)

    def create_defaults(self):
        # Default service config
        self.service_config['name'] = 'LoggingService'
        self.service_config['hostname'] = '127.0.0.1'
        self.service_config['port'] = 4041
        self.service_config['debug_mode'] = True

        # Default backend configuration
        self.backend_config['hostname'] = '127.0.0.1'
        self.backend_config['port'] = 40075

        # Default redis configuration
        self.redis_config['hostname'] = '127.0.0.1'
        self.redis_config['port'] = 6379
        self.redis_config['username'] = ''
        self.redis_config['password'] = ''
        self.redis_config['db'] = 0

        # Default database configuration
        self.db_config['db_type'] = 'ram'
        self.db_config['name'] = 'openteralogs'
        self.db_config['url'] = '127.0.0.1'
        self.db_config['port'] = 5432
        self.db_config['username'] = ''
        self.db_config['password'] = ''

        # Default logging configuration
        self.logging_config['level'] = 'trace'

