import uuid

from requests import Response
from flask import request


class TeraServiceClient:

    def __init__(self, token_dict: dict, token: str, config_man):
        self.__service_uuid = token_dict['service_uuid']
        self.__service_token = token

        # A little trick here to get the right URL for the server if we are using a proxy
        backend_hostname = config_man.backend_config["hostname"]
        backend_port = str(config_man.backend_config["port"])

        if 'X-Externalhost' in request.headers:
            backend_hostname = request.headers['X-Externalhost']

        if 'X-Externalport' in request.headers:
            backend_port = request.headers['X-Externalport']

        self.__backend_url = 'https://' + backend_hostname + ':' + backend_port

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

    def do_get_request_to_backend(self, path: str) -> Response:
        from requests import get
        request_headers = {'Authorization': 'OpenTera ' + self.__service_token}
        # TODO: remove verify=False and check certificate
        backend_response = get(url=self.__backend_url + path, headers=request_headers, verify=False)
        return backend_response

    def __repr__(self):
        return '<TeraServiceClient - UUID: ' + self.__service_uuid \
               + ', Token: ' + self.__service_token + '>'
