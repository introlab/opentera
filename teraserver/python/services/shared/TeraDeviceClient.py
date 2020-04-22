import uuid

from requests import Response
from flask import request


class TeraDeviceClient:

    def __init__(self, u_uuid: uuid, token: str, config_man):
        self.__device_uuid = u_uuid
        self.__device_token = token

        # A little trick here to get the right URL for the server if we are using a proxy
        backend_hostname = config_man.backend_config["hostname"]
        backend_port = str(config_man.backend_config["port"])

        if 'X-Externalhost' in request.headers:
            backend_hostname = request.headers['X-Externalhost']

        if 'X-Externalport' in request.headers:
            backend_port = request.headers['X-Externalport']

        self.__backend_url = 'https://' + backend_hostname + ':' + backend_port

        import os

        # TODO Certificates should be from proxy?
        self.__backend_cacert = os.path.join(config_man.server_config["ssl_path"],
                                             config_man.server_config["site_certificate"])

    @property
    def device_uuid(self):
        return self.__device_uuid

    @device_uuid.setter
    def device_uuid(self, u_uuid: uuid):
        self.__device_uuid = u_uuid

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

    def __repr__(self):
        return '<TeraDeviceClient - UUID: ' + self.__device_token \
               + ', Token: ' + self.__device_token + '>'
