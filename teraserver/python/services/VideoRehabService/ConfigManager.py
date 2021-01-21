from opentera.services.ServiceConfigManager import ServiceConfigManager, WebRTCConfig


# Build configuration from base classes
class ConfigManager(ServiceConfigManager, WebRTCConfig):
    def validate_config(self, config_json):
        return super().validate_config(config_json) and self.validate_webrtc_config(config_json)


