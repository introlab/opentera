from opentera.services.ServiceConfigManager import ServiceConfigManager, DBConfig


class FileTransferConfig:
    filetransfer_config = {}

    def __init__(self):
        pass

    def validate_filetransfer_config(self, config: dict):
        if 'FileTransfer' in config:
            required_fields = ['files_directory']
            for field in required_fields:
                if field not in config['FileTransfer']:
                    print('ERROR: FileTransferConfig - missing field :' + field)
                    return False

            # Every field is present, update configuration
            self.filetransfer_config = config['FileTransfer']
            return True
        # Invalid
        return False


# Build configuration from base classes
class ConfigManager(ServiceConfigManager, FileTransferConfig, DBConfig):
    def validate_config(self, config_json):
        return super().validate_config(config_json) \
               and self.validate_filetransfer_config(config_json) and self.validate_database_config(config_json)

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
        self.db_config['name'] = 'openterafiles'
        self.db_config['url'] = '127.0.0.1'
        self.db_config['port'] = 5432
        self.db_config['username'] = ''
        self.db_config['password'] = ''

        # Default logging configuration
        self.logging_config['level'] = 'trace'
