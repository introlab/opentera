import json
from services.shared.ServiceConfigManager import ServiceConfigManager, DBConfig


class ConfigManager(ServiceConfigManager, DBConfig):
    def validate_config(self, config_json):
        return super().validate_config(config_json) and self.validate_database_config(config_json)

