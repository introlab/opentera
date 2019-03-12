import json


class ConfigManager:

    server_config = {}  # name, port, ssl_path
    db_config = {}      # name, url, port, username, password

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

    @staticmethod
    def validate_server_config(config):
        rval = True
        required_fields = ['name', 'port', 'ssl_path']
        for field in required_fields:
            if field not in config:
                print('ERROR: Server Config - missing server ' + field)
        return rval

    @staticmethod
    def validate_database_config(config):
        rval = True
        required_fields = ['name', 'port', 'url', 'username', 'password']
        for field in required_fields:
            if field not in config:
                print('ERROR: Database Config - missing database ' + field)
        return rval
