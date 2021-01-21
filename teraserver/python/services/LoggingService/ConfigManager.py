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
    def validate_config(self, config_json):
        return super().validate_config(config_json) \
               and self.validate_logging_config(config_json) and self.validate_database_config(config_json)


