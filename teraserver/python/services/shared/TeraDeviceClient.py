import uuid

from requests import Response
from flask import request


class TeraDeviceClient:

    def __init__(self, token_dict: dict, token: str, config_man):
        self.__device_uuid = token_dict['device_uuid']
        self.__id_device = token_dict['id_device']
        self.__device_token = token

        # A little trick here to get the right URL for the server if we are using a proxy
        backend_hostname = config_man.backend_config["hostname"]
        backend_port = str(config_man.backend_config["port"])

        if 'X-Externalhost' in request.headers:
            backend_hostname = request.headers['X-Externalhost']

        if 'X-Externalport' in request.headers:
            backend_port = request.headers['X-Externalport']

        self.__backend_url = 'https://' + backend_hostname + ':' + backend_port


    @property
    def device_uuid(self):
        return self.__device_uuid

    @device_uuid.setter
    def device_uuid(self, u_uuid: uuid):
        self.__device_uuid = u_uuid

    @property
    def id_device(self):
        return self.__id_device

    @id_device.setter
    def id_device(self, id_dev: int):
        self.__id_device = id_dev

    @property
    def device_token(self):
        return self.__device_token

    @device_token.setter
    def device_token(self, token: str):
        self.__device_token = token

    def do_get_request_to_backend(self, path: str) -> Response:
        from requests import get
        request_headers = {'Authorization': 'OpenTera ' + self.__device_token}
        # TODO: remove verify=False and check certificate
        backend_response = get(url=self.__backend_url + path, headers=request_headers, verify=False)
        return backend_response

    def can_access_session(self, id_session: int) -> bool:
        response = self.do_get_request_to_backend('/api/device/sessions?id_session=' + str(id_session))
        return response.status_code == 200

    def get_device_infos(self) -> dict:
        response = self.do_get_request_to_backend('/api/device/devices')
        if response.status_code == 200:
            return response.json()
        return {}

    def __repr__(self):
        return '<TeraDeviceClient - UUID: ' + self.__device_token \
               + ', Token: ' + self.__device_token + '>'
