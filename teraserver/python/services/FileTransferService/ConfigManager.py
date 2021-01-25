from opentera.services.ServiceConfigManager import ServiceConfigManager, DBConfig


class FileTransferConfig:
    filetransfer_config = {}

    def __init__(self):
        pass

    def validate_filetransfer_config(self, config: dict):
        if 'FileTransfer' in config:
            required_fields = ['upload_directory']
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


