import uuid

from requests import Response
from flask import request


class TeraServiceClient:

    def __init__(self, token_dict: dict, token: str, config_man, service):
        self.__service_uuid = token_dict['service_uuid']
        self.__service_token = token
        self.__service = service

    @property
    def service_uuid(self):
        return self.__service_uuid

    @service_uuid.setter
    def service_uuid(self, s_uuid: uuid):
        self.__service_uuid = s_uuid

    @property
    def service_token(self):
        return self.__service_token

    @service_token.setter
    def service_token(self, token: str):
        self.__service_token = token

    def do_get_request_to_backend(self, path: str, params: dict = None, override_token: str | None = None) -> Response:
        """
        Now using service function:
        def get_from_opentera_with_token(self, token: str, api_url: str, params: dict = {},
                                     additional_headers: dict = {}) -> Response:
        """
        if params is None:
            params = {}

        token = self.__service_token
        if override_token:
            token = override_token

        return self.__service.get_from_opentera_with_token(token, api_url=path, params=params)

    def get_service_infos(self) -> dict:
        params = {'uuid_service': self.__service_uuid}
        response = self.do_get_request_to_backend('/api/service/services', params)
        if response.status_code == 200:
            return response.json()[0]
        return {}

    def __repr__(self):
        return '<TeraServiceClient - UUID: ' + self.__service_uuid \
               + ', Token: ' + self.__service_token + '>'
