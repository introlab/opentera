import json


class ConfigManager:

    server_config = {}  # name, port, ssl_path
    db_config = {}      # name, url, port, username, password
    redis_config = {}
    backend_config = {}

    def __init__(self):
        pass

    def load_config(self, filename):
        try:
            config_file = open(filename, mode='rt', encoding='utf8')

        except IOError:
            print("Error loading file: " + filename)
            return

        raw_text = config_file.read()
        config_file.close()

        # Strip UTF8 BOM, if needed
        if not raw_text.startswith('{'):
            raw_text = raw_text[1:]
        config_json = json.loads(raw_text)

        if self.validate_server_config(config_json['Server']):
            self.server_config = config_json["Server"]

        if self.validate_database_config(config_json['Database']):
            self.db_config = config_json["Database"]

        if self.validate_redis_config(config_json['Redis']):
            self.redis_config = config_json["Redis"]

        if self.validate_backend_config(config_json['Backend']):
            self.backend_config = config_json["Backend"]


    @staticmethod
    def validate_server_config(config):
        rval = True

        required_fields = ['name', 'port', 'ssl_path', 'hostname',
                           'site_certificate', 'site_private_key', 'ca_certificate', 'ca_private_key']
        for field in required_fields:
            if field not in config:
                print('ERROR: Server Config - missing server ' + field)
                rval = False
        return rval

    @staticmethod
    def validate_database_config(config):
        rval = True
        required_fields = ['name', 'port', 'url', 'username', 'password']
        for field in required_fields:
            if field not in config:
                print('ERROR: Database Config - missing database ' + field)
                rval = False
        return rval

    @staticmethod
    def validate_redis_config(config):
        """
        :param config:
        :return:
        """
        rval = True
        required_fields = ['hostname', 'port', 'db', 'username', 'password']
        for field in required_fields:
            if field not in config:
                print('ERROR: Redis Config - missing database ' + field)
                rval = False
        return rval

    @staticmethod
    def validate_backend_config(config):
        rval = True
        required_fields = ['hostname', 'port', 'secure_key']
        for field in required_fields:
            if field not in config:
                print('ERROR: Backend Config - missing field ' + field)
                rval = False
        return True
