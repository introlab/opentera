import json


class WebRTCConfig:
    webrtc_config = {}

    def __init__(self):
        pass

    def validate_webrtc_config(self, config: dict):
        if 'WebRTC' in config:
            required_fields = ['hostname', 'working_directory', 'executable', 'script']
            for field in required_fields:
                if field not in config['WebRTC']:
                    print('ERROR: WebRTC Config - missing field :' + field)
                    return False

            # Every field is present, update configuration
            self.webrtc_config = config['WebRTC']
            return True
        # Invalid
        return False


class RedisConfig:
    redis_config = {}

    def __init__(self):
        pass

    def validate_redis_config(self, config: dict):
        if 'Redis' in config:
            required_fields = ['hostname', 'port', 'db', 'username', 'password']
            for field in required_fields:
                if field not in config['Redis']:
                    print('ERROR: Redis Config - missing field : ' + field)
                    return False

            self.redis_config = config['Redis']
            return True
        # Invalid
        return False


class DBConfig:
    db_config = {}

    def __init__(self):
        pass

    def validate_database_config(self, config: dict):
        if 'Database' in config:
            required_fields = ['name', 'port', 'url', 'username', 'password']
            for field in required_fields:
                if field not in config['Database']:
                    print('ERROR: Database Config - missing field : ' + field)
                    return False
            self.db_config = config['Database']
            return True
        # Invalid
        return False


class BackendConfig:
    backend_config = {}

    def validate_backend_config(self, config: dict):
        if 'Backend' in config:
            required_fields = ['hostname', 'port']
            for field in required_fields:
                if field not in config['Backend']:
                    print('ERROR: Backend Config - missing field :' + field)
                    return False

            self.backend_config = config['Backend']
            return True
        # Invalid
        return False


class ServiceConfig:
    service_config = {}

    def validate_service_config(self, config):

        if 'Service' in config:
            required_fields = ['name', 'port', 'hostname']
            for field in required_fields:
                if field not in config['Service']:
                    print('ERROR: Service Config - missing field ' + field)
                    return False
            self.service_config = config['Service']

            # Optional fields
            if 'debug_mode' not in self.service_config:
                self.service_config['debug_mode'] = False

            return True
        # Invalid
        return False


# Base configuration needs ServiceConfig, RedisConfig, BackendConfig
class ServiceConfigManager(ServiceConfig, RedisConfig, BackendConfig):

    def __init__(self):
        # Initialize base class
        ServiceConfig.__init__(self)
        RedisConfig.__init__(self)
        BackendConfig.__init__(self)

    def load_config(self, filename):
        try:
            config_file = open(filename, mode='rt', encoding='utf8')

        except IOError:
            print("Error opening file: " + filename)
            return False

        try:
            # Read json from file
            config_json = json.load(config_file)
        except json.JSONDecodeError as e:
            print('Error reading file : ', filename, e)
            return False

        config_file.close()

        # call validate config
        # this function needs to be overloaded if you derive from ServiceConfigManager
        return self.validate_config(config_json)

    def validate_config(self, config_json):

        # Validate service configuration
        if not self.validate_service_config(config_json):
            return False

        # Validate redis configuration
        if not self.validate_redis_config(config_json):
            return False

        # Validate backend configuration
        if not self.validate_backend_config(config_json):
            return False

        # Everything went well
        return True







