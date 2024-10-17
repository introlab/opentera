from opentera.services.ServiceConfigManager import ServiceConfigManager, DBConfig


class EmailConfig:
    email_config = {}

    def __init__(self):
        pass

    def validate_email_config(self, config: dict):
        if 'Email' in config:
            required_fields = ['hostname', 'port', 'tls', 'ssl', 'username', 'password']
            for field in required_fields:
                if field not in config['Email']:
                    print('ERROR: Email Config - missing field :' + field)
                    return False

            # Every field is present, update configuration
            self.email_config = config['Email']
            return True
        # Invalid
        return False


# Build configuration from base classes
class ConfigManager(ServiceConfigManager, EmailConfig, DBConfig):
    # Only useful for tests
    server_config = {}

    def to_dict(self):
        return {
            'Service': self.service_config,
            'Backend': self.backend_config,
            'Redis': self.redis_config,
            'Email': self.email_config,
            'Database': self.db_config
        }

    def validate_config(self, config_json: dict):
        return super().validate_config(config_json) \
               and self.validate_email_config(config_json) and self.validate_database_config(config_json)

    def create_defaults(self):
        # Default service config
        self.service_config['name'] = 'EmaiLService'
        self.service_config['hostname'] = '127.0.0.1'
        self.service_config['port'] = 4043
        self.service_config['debug_mode'] = True
        self.service_config['ServiceUUID'] = 'invalid'

        # Default backend configuration
        self.backend_config['hostname'] = '127.0.0.1'
        self.backend_config['port'] = 40075

        # Default redis configuration
        self.redis_config['hostname'] = '127.0.0.1'
        self.redis_config['port'] = 6379
        self.redis_config['username'] = ''
        self.redis_config['password'] = ''
        self.redis_config['db'] = 0

        # Default email server configuration
        self.email_config['hostname'] = '127.0.0.1'
        self.email_config['port'] = 25
        self.email_config['tls'] = False
        self.email_config['ssl'] = True
        self.email_config['username'] = ''
        self.email_config['password'] = ''

        # Default database configuration
        self.db_config['db_type'] = 'ram'
        self.db_config['name'] = 'openteraemails'
        self.db_config['url'] = '127.0.0.1'
        self.db_config['port'] = 5432
        self.db_config['username'] = ''
        self.db_config['password'] = ''

        # For tests
        self.server_config['hostname'] = self.backend_config['hostname']
        self.server_config['port'] = self.backend_config['port']


