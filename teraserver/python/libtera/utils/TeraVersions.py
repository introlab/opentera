from libtera.db.models.TeraServerSettings import TeraServerSettings
from OpenTeraServerVersion import opentera_server_version_string
import json


class TeraVersions:
    def __init__(self):
        self.settings = {}

    @property
    def server_version_string(self):
        if 'server_version_string' in self.settings:
            return self.settings['server_version_string']
        return ''

    @server_version_string.setter
    def server_version_string(self, version: str):
        self.settings['server_version_string'] = version

    def save_to_db(self):
        TeraServerSettings.set_server_setting(TeraServerSettings.ServerVersions, json.dumps(self.settings))

    def load_from_db(self):
        settings = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerVersions)
        if settings:
            self.settings = json.loads(settings)

    def __repr__(self):
        return '<TeraVersions: ' + json.dumps(self.settings) + ' >'


if __name__ == '__main__':
    versions = TeraVersions()
    versions.server_version_string = 'rien'
    print(versions, versions.server_version_string)