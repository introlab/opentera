from opentera.db.models.TeraServerSettings import TeraServerSettings
from opentera import OpenTeraServerVersion
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
            self.client_name = value['client_name']
        if 'client_description' in value:
            self.client_description = value['client_description']
        if 'client_version' in value:
            self.client_version = value['client_version']
        if 'client_documentation_url' in value:
            self.client_documentation_url = value['client_documentation_url']
        if 'client_windows_download_url' in value:
            self.client_windows_download_url = value['client_windows_download_url']
        if 'client_mac_download_url' in value:
            self.client_mac_download_url = value['client_mac_download_url']
        if 'client_linux_download_url' in value:
            self.client_linux_download_url = value['client_linux_download_url']

    def to_dict(self):
        return {'client_name': self.client_name,
                'client_description': self.client_description,
                'client_version': self.client_version,
                'client_documentation_url': self.client_documentation_url,
                'client_windows_download_url': self.client_windows_download_url,
                'client_mac_download_url': self.client_mac_download_url,
                'client_linux_download_url': self.client_linux_download_url}

    @classmethod
    def get_json_schema(cls):
        model_name = cls.__name__
        # Properties dict
        pr_dict = dict()
        # Fill properties
        pr_dict['client_name'] = {'type': 'string', 'required': True}
        pr_dict['client_description'] = {'type': 'string', 'required': True}
        pr_dict['client_version'] = {'type': 'string', 'required': True}
        pr_dict['client_documentation_url'] = {'type': 'string', 'required': True}
        pr_dict['client_windows_download_url'] = {'type': 'string', 'required': False}
        pr_dict['client_mac_download_url'] = {'type': 'string', 'required': False}
        pr_dict['client_linux_download_url'] = {'type': 'string', 'required': False}

        schema = {model_name: {'properties': pr_dict, 'type': 'object'}}
        return schema

    def __repr__(self):
        return '<ClientVersions ' + json.dumps(self.to_dict()) + ' >'


class TeraVersions:
    def __init__(self):
        self.server_version = str(OpenTeraServerVersion.opentera_server_version_string)
        self.server_major_version = OpenTeraServerVersion.opentera_server_major_version
        self.server_minor_version = OpenTeraServerVersion.opentera_server_minor_version
        self.server_patch_version = OpenTeraServerVersion.opentera_server_patch_version
        self.clients = dict()
        # Hard coding OpenTeraPlus for now
        # Will be overwritten if necessary
        self.clients['OpenTeraPlus'] = ClientVersions(client_name='OpenTeraPlus',
                                                      client_description='OpenTeraPlus Qt Client',
                                                      client_version='1.0.0',
                                                      client_documentation_url=
                                                      'https://github.com/introlab/openteraplus')

    def get_client_version_with_name(self, name: str):
        if name in self.clients:
            return self.clients[name]
        return None

    def set_client_version_with_name(self, name: str, client_version: ClientVersions):
        self.clients[name] = client_version

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
    def client_dict(self):
        return self.clients

    def to_dict(self) -> dict:
        output = {'version_string': self.server_version,
                  'version_major': self.server_major_version,
                  'version_minor': self.server_minor_version,
                  'version_patch': self.server_patch_version,
                  'clients': {}}
        # Output clients dict
        for client_name in self.clients:
            output['clients'][client_name] = self.clients[client_name].to_dict()
        return output

    def from_dict(self, value: dict):
        # We do not want to load version from DB
        # TODO can we do better ?
        # if 'version_string' in value:
        #     self.server_version = value['version_string']
        # if 'version_major' in value:
        #     self.server_major_version = value['version_major']
        # if 'version_minor' in value:
        #     self.server_minor_version = value['version_minor']
        # if 'version_patch' in value:
        #     self.server_patch_version = value['version_patch']
        if 'clients' in value:
            # We have a list of clients dict in value['clients']
            # Make sure we have a dict and not a list (in old implementation)
            if isinstance(value['clients'], dict):
                for client_name in value['clients']:
                    client_version = ClientVersions()
                    client_version.from_dict(value['clients'][client_name])
                    # Put in the dict, overwriting if client have the same name
                    # TODO can we do better?
                    self.clients[client_version.client_name] = client_version

    def save_to_db(self):
        TeraServerSettings.set_server_setting(TeraServerSettings.ServerVersions, json.dumps(self.to_dict()))

    def load_from_db(self):
        settings = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerVersions)
        if settings:
            self.from_dict(json.loads(settings))
            return True
        return False

    def __repr__(self):
        return '<TeraVersions: ' + json.dumps(self.to_dict()) + ' >'


# if __name__ == '__main__':
#     versions = TeraVersions()
#     versions_dict = versions.to_dict()
#     versions2 = TeraVersions()
#     versions2.from_dict(versions_dict)
#     print(versions.get_client_version_with_name('OpenTeraPlus'))
#     print(versions.get_client_version_with_name('Unknown'))
#     print(versions)
#     print(versions2)
#     print(ClientVersions.get_json_schema())
