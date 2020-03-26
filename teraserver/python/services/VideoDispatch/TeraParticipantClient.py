import uuid
from services.VideoDispatch.Globals import config_man
from requests import Response


class TeraParticipantClient:

    def __init__(self, u_uuid: uuid, token: str):
        self.__participant_uuid = u_uuid
        self.__participant_token = token

        self.__backend_url = 'https://' + config_man.backend_config["hostname"] + ':' + \
                             str(config_man.backend_config["port"])
        import os

        self.__backend_cacert = os.path.join(config_man.server_config["ssl_path"],
                                             config_man.server_config["site_certificate"])

    @property
    def participant_uuid(self):
        return self.__participant_uuid

    @participant_uuid.setter
    def participant_uuid(self, u_uuid: uuid):
        self.__participant_uuid = u_uuid

    @property
    def participant_token(self):
        return self.__participant_token

    @participant_token.setter
    def participant_token(self, token: str):
        self.__participant_token = token

    def do_get_request_to_backend(self, path: str) -> Response:
        from requests import get
        request_headers = {'Authorization': 'OpenTera ' + self.__partipant_token}
        # TODO: remove verify=False and check certificate
        backend_response = get(url=self.__backend_url + path, headers=request_headers, verify=False)
        return backend_response

    def __repr__(self):
        return '<TeraParticipantClient - UUID: ' + self.__participant_uuid \
               + ', Token: ' + self.__participant_token + '>'
