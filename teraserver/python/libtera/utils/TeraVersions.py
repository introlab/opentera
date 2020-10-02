from libtera.db.models.TeraServerSettings import TeraServerSettings
import OpenTeraServerVersion
import json


class ClientVersions:
    def __init__(self, **kwargs):
        self.name = kwargs.get('client_name', None)
        self.description = kwargs.get('client_description', None)
        self.version = kwargs.get('client_version', None)
        self.documentation_url = kwargs.get('client_documentation_url', None)
        self.windows_download_url = kwargs.get('client_windows_download_url', None)
        self.mac_download_url = kwargs.get('client_mac_download_url', None)
        self.linux_download_url = kwargs.get('client_linux_download_url', None)

    @property
    def client_name(self):
        return self.name

    @client_name.setter
    def client_name(self, name: str):
        self.name = name

    @property
    def client_description(self):
        return self.description

    @client_description.setter
    def client_description(self, description: str):
        self.description = description

    @property
    def client_version(self):
        return self.version

    @client_version.setter
    def client_version(self, version: str):
        self.version = version

    @property
    def client_documentation_url(self):
        return self.documentation_url

    @client_documentation_url.setter
    def client_documentation_url(self, value: str):
        self.documentation_url = value

    @property
    def client_windows_download_url(self):
        return self.windows_download_url

    @client_windows_download_url.setter
    def client_windows_download_url(self, value: str):
        self.windows_download_url = value

    @property
    def client_mac_download_url(self):
        return self.mac_download_url

    @client_mac_download_url.setter
    def client_mac_download_url(self, value: str):
        self.mac_download_url = value

    @property
    def client_linux_download_url(self):
        return self.linux_download_url

    @client_linux_download_url.setter
    def client_linux_download_url(self, value: str):
        self.linux_download_url = value

    def from_dict(self, value: dict):
        if 'client_name' in value:
            self.name = value['client_name']
        if 'client_description' in value:
            self.description = value['client_description']
        if 'client_version' in value:
            self.version = value['client_version']
        if 'client_documentation_url' in value:
            self.documentation_url = value['client_documentation_url']
        if 'client_windows_download_url' in value:
            self.description = value['client_windows_download_url']
        if 'client_mac_download_url' in value:
            self.version = value['client_mac_download_url']
        if 'client_linux_download_url' in value:
            self.documentation_url = value['client_linux_download_url']

    def to_dict(self):
        return {'client_name': self.name,
                'client_description': self.description,
                'client_version': self.version,
                'client_documentation_url': self.documentation_url,
                'client_windows_download_url': self.windows_download_url,
                'client_mac_download_url': self.mac_download_url,
                'client_linux_download_url': self.linux_download_url}

    def __repr__(self):
        return '<ClientVersions ' + self.name + str(self.version) + ' >'


class TeraVersions:
    def __init__(self):
        self.server_version = str(OpenTeraServerVersion.opentera_server_version_string)
        self.server_major_version = OpenTeraServerVersion.opentera_server_major_version
        self.server_minor_version = OpenTeraServerVersion.opentera_server_minor_version
        self.server_patch_version = OpenTeraServerVersion.opentera_server_patch_version
        self.clients = list()
        # Hard coding OpenTeraPlus for now
        self.clients.append(ClientVersions(client_name='OpenTeraPlus',
                                           client_version='0.1.0',
                                           client_documentation_url='https://github.com/introlab/openteraplus'))

    @property
    def version_string(self):
        return self.server_version

    @property
    def major_version(self):
        return self.server_major_version

    @property
    def minor_version(self):
        return self.server_minor_version

    @property
    def patch_version(self):
        return self.server_patch_version

    @property
    def client_list(self):
        return self.clients

    def to_dict(self) -> dict:
        output = {'version_string': self.server_version,
                  'version_major': self.server_major_version,
                  'version_minor': self.server_minor_version,
                  'version_patch': self.server_patch_version,
                  'clients': []}
        for client in self.clients:
            output['clients'].append(client.to_dict())
        return output

    def from_dict(self, value: dict):
        # We do not want to load version from DB
        # TODO can we do better
        # if 'version_string' in value:
        #     self.server_version = value['version_string']
        # if 'version_major' in value:
        #     self.server_major_version = value['version_major']
        # if 'version_minor' in value:
        #     self.server_minor_version = value['version_minor']
        # if 'version_patch' in value:
        #     self.server_patch_version = value['version_patch']
        if 'clients' in value:
            for client_dict in value['clients']:
                client = ClientVersions()
                client.from_dict(client_dict)
                self.clients.append(client)

    def save_to_db(self):
        TeraServerSettings.set_server_setting(TeraServerSettings.ServerVersions, json.dumps(self.to_dict()))

    def load_from_db(self):
        settings = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerVersions)
        self.from_dict(json.loads(settings))

    def __repr__(self):
        return '<TeraVersions: ' + json.dumps(self.to_dict()) + ' >'


# if __name__ == '__main__':
#     versions = TeraVersions()
#     versions_dict = versions.to_dict()
#     versions2 = TeraVersions()
#     versions2.from_dict(versions_dict)
#     print(versions)
#     print(versions2)
