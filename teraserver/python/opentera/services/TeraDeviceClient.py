import uuid

from requests import Response
from flask import request


class TeraDeviceClient:

    def __init__(self, token_dict: dict, token: str, config_man, service):
        self.__device_uuid = token_dict['device_uuid']
        self.__id_device = token_dict['id_device']
        self.__device_token = token
        self.__service = service

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

    def do_get_request_to_backend(self, path: str, params: dict = None) -> Response:
        """
        Now using service function:
        def get_from_opentera_with_token(self, token: str, api_url: str, params: dict = {},
                                     additional_headers: dict = {}) -> Response:
        """
        if params is None:
            params = {}
        return self.__service.get_from_opentera_with_token(self.__device_token, api_url=path, params=params)

    def can_access_session(self, id_session: int) -> bool:
        params = {'id_session': str(id_session)}
        response = self.do_get_request_to_backend('/api/device/sessions', params)
        return response.status_code == 200

    def get_device_infos(self) -> dict:
        response = self.do_get_request_to_backend('/api/device/devices')
        if response.status_code == 200:
            return response.json()
        return {}

    def __repr__(self):
        return '<TeraDeviceClient - UUID: ' + self.__device_token \
               + ', Token: ' + self.__device_token + '>'
