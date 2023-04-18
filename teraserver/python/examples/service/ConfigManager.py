from opentera.services.ServiceConfigManager import ServiceConfigManager, DBConfig


# TODO: Rename "ExampleService" and "ExampleServiceConfig" to something more appropriate for your own service
class ExampleServiceConfig:
    specific_service_config = {}

    def __init__(self):
        pass

    def validate_specific_service_config(self, config: dict):
        # TODO: Create an entry specific for that service in the json config file and properly manage here the settings
        #  For now, only "files_directory" which will hold the files is defined.
        if 'ExampleService' in config:
            required_fields = ['files_directory']
            for field in required_fields:
                if field not in config['ExampleService']:
                    print('ERROR: ExampleService Config - missing field :' + field)
                    return False

            # Every field is present, update configuration
            # TODO: Rename "ExampleService" to the correct value
            self.specific_service_config = config['ExampleService']
            return True
        # Invalid
        return False


# Build configuration from base classes
# TODO: Adjust ExampleServiceConfig base class name here.
# TODO: Modify (and rename) "ExampleService.json" file accordingly with the recommandations below
class ConfigManager(ServiceConfigManager, ExampleServiceConfig, DBConfig):
    def validate_config(self, config_json):
        return super().validate_config(config_json) \
               and self.validate_service_config(config_json) and self.validate_database_config(config_json) and \
               self.validate_specific_service_config(config_json)

    def create_defaults(self):
        # Default service config
        # TODO: Adjust ExampleService correct name (service key in OpenTera server)
        self.service_config['name'] = 'ExampleService'
        self.service_config['hostname'] = '127.0.0.1'
        # TODO: Select a different available port. See nginx config in "config/opentera.conf" in the "proxy_pass" lines
        #  to see used ports
        self.service_config['port'] = 5010
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
        self.db_config['db_type'] = 'QPSQL'
        # TODO: Set correct database name as default
        self.db_config['name'] = 'openteraexampleservice'
        self.db_config['url'] = '127.0.0.1'
        self.db_config['port'] = 5432
        self.db_config['username'] = ''
        self.db_config['password'] = ''

        self.specific_service_config['files_directory'] = 'files'
