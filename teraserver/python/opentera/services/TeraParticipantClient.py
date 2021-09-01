import uuid

from requests import Response
from flask import request
from opentera.redis.RedisRPCClient import RedisRPCClient


class TeraParticipantClient:

    def __init__(self, token_dict: dict, token: str, config_man):
        self.__participant_uuid = token_dict['participant_uuid']
        self.__id_participant = token_dict['id_participant']
        self.__participant_token = token

        # A little trick here to get the right URL for the server if we are using a proxy
        backend_hostname = config_man.backend_config["hostname"]
        backend_port = str(config_man.backend_config["port"])

        if 'X-Externalhost' in request.headers:
            backend_hostname = request.headers['X-Externalhost']

        if 'X-Externalport' in request.headers:
            backend_port = request.headers['X-Externalport']

        self.__backend_url = 'https://' + backend_hostname + ':' + backend_port
        self.__config_man = config_man
        self.__rpc_client = RedisRPCClient(config_man.redis_config)

    @property
    def participant_uuid(self):
        return self.__participant_uuid

    @participant_uuid.setter
    def participant_uuid(self, u_uuid: uuid):
        self.__participant_uuid = u_uuid

    @property
    def id_participant(self):
        return self.__id_participant

    @id_participant.setter
    def id_participant(self, id_p: int):
        self.__id_participant = id_p

    @property
    def participant_token(self):
        return self.__participant_token

    @participant_token.setter
    def participant_token(self, token: str):
        self.__participant_token = token

    def get_participant_infos(self) -> dict:
        # Get information from service rpc function since participant has no rights from the participants api
        #participant_info = self.__rpc_client.call_service(self.__config_man.service_config['name'],
        #                                                  'participant_info', self.__participant_uuid)
        #return participant_info

        response = self.do_get_request_to_backend('/api/participant/participants')
        if response.status_code == 200:
            return response.json()
        return {}

    def do_get_request_to_backend(self, path: str) -> Response:
        from requests import get
        request_headers = {'Authorization': 'OpenTera ' + self.__participant_token}
        # TODO: remove verify=False and check certificate
        backend_response = get(url=self.__backend_url + path, headers=request_headers, verify=False)
        return backend_response

    def __repr__(self):
        return '<TeraParticipantClient - UUID: ' + self.__participant_uuid \
               + ', Token: ' + self.__participant_token + '>'
