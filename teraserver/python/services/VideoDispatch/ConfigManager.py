from services.shared.ServiceConfigManager import ServiceConfigManager, WebRTCConfig, DBConfig


# Build configuration from base classes
class ConfigManager(ServiceConfigManager, WebRTCConfig, DBConfig):
    def validate_config(self, config_json):
        return super().validate_config(config_json) \
               and self.validate_webrtc_config(config_json) and self.validate_database_config(config_json)


