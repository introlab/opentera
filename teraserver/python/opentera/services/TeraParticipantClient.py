import uuid

from requests import Response
from flask import request
from opentera.redis.RedisRPCClient import RedisRPCClient


class TeraParticipantClient:

    def __init__(self, token_dict: dict, token: str, config_man, service):
        self.__participant_uuid = token_dict['participant_uuid']
        self.__id_participant = token_dict['id_participant']
        self.__participant_token = token
        self.__service = service

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
        response = self.do_get_request_to_backend('/api/participant/participants')
        if response.status_code == 200:
            return response.json()
        return {}

    def do_get_request_to_backend(self, path: str, params: dict=None) -> Response:
        """
        Now using service function:
        def get_from_opentera_with_token(self, token: str, api_url: str, params: dict = {},
                                     additional_headers: dict = {}) -> Response:
        """
        if params is None:
            params = {}
        return self.__service.get_from_opentera_with_token(self.__participant_token, api_url=path, params=params)

    def __repr__(self):
        return '<TeraParticipantClient - UUID: ' + self.__participant_uuid \
               + ', Token: ' + self.__participant_token + '>'
