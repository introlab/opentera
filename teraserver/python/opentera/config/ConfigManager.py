import json


class ConfigManager:

    server_config = {}  # name, port, ssl_path
    db_config = {}      # name, url, port, username, password
    redis_config = {}

    def __init__(self):
        pass

    def load_config(self, filename):
        try:
            config_file = open(filename, mode='rt', encoding='utf8')
            config_json = json.load(config_file)
            config_file.close()
        except IOError as e:
            print("Error loading file: " + filename, e)
            return

        except json.JSONDecodeError as e:
            print("Error loading json file: ", filename, e)
            return

        if self.validate_server_config(config_json['Server']):
            self.server_config = config_json["Server"]

        if self.validate_database_config(config_json['Database']):
            self.db_config = config_json["Database"]

        if self.validate_redis_config(config_json['Redis']):
            self.redis_config = config_json["Redis"]

    def create_defaults(self):
        # Server fake config
        server_required_fields = ['name', 'port', 'use_ssl', 'ssl_path', 'hostname', 'site_certificate',
                                  'site_private_key', 'ca_certificate', 'ca_private_key', 'upload_path',
                                  'enable_docs']

        for field in server_required_fields:
            self.server_config[field] = ''

        self.server_config['upload_path'] = 'uploads'
        self.server_config['hostname'] = '127.0.0.1'
        self.server_config['port'] = 4040
        self.server_config['enable_docs'] = True

        # Database fake config
        database_required_fields = ['name', 'port', 'url', 'username', 'password']
        for field in database_required_fields:
            self.db_config[field] = ''

        # Redis fake config
        redis_required_fields = ['hostname', 'port', 'db', 'username', 'password']
        for field in redis_required_fields:
            self.redis_config[field] = ''
        # Default redis configuration
        self.redis_config['hostname'] = '127.0.0.1'
        self.redis_config['port'] = 6379
        # Already set to empty string previously
        self.redis_config['username'] = ''
        self.redis_config['password'] = ''
        self.redis_config['db'] = 0

    @staticmethod
    def validate_server_config(config):
        rval = True

        required_fields = ['name', 'port', 'use_ssl', 'ssl_path', 'hostname',
                           'site_certificate', 'site_private_key', 'ca_certificate', 'ca_private_key', 'upload_path']
        for field in required_fields:
            if field not in config:
                print('ERROR: Server Config - missing server ' + field)
                rval = False

        # Add optional debug flag
        if 'debug_mode' not in config:
            config['debug_mode'] = False

        # Add optional enable docs
        if 'enable_docs' not in config:
            config['enable_docs'] = False

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
    def validate_service_config(service_name, config):
        """
       :param config:
       :return:
       """
        rval = True
        # TODO make sure to update the fields
        required_fields = ['ServiceUUID', 'ServiceHostname', 'ServicePort', 'ServiceEndpoint', 'ClientEndpoint']
        for field in required_fields:
            if field not in config:
                print('ERROR: Service Config - missing config field  in service', service_name, ' field:', field)
                rval = False
        return rval
