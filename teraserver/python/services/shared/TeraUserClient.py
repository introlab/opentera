import uuid
from flask import request
from requests import Response


class TeraUserClient:

    def __init__(self, u_uuid: uuid, token: str, config_man):
        self.__user_uuid = u_uuid
        self.__user_token = token

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
    def user_uuid(self):
        return self.__user_uuid

    @user_uuid.setter
    def user_uuid(self, u_uuid: uuid):
        self.__user_uuid = u_uuid

    @property
    def user_token(self):
        return self.__user_token

    @user_token.setter
    def user_token(self, token: str):
        self.__user_token = token

    def do_get_request_to_backend(self, path: str) -> Response:
        from requests import get
        request_headers = {'Authorization': 'OpenTera ' + self.__user_token}
        # TODO: remove verify=False and check certificate
        backend_response = get(url=self.__backend_url + path, headers=request_headers, verify=False)
        return backend_response

    def get_role_for_site(self, id_site: int):
        response = self.do_get_request_to_backend('/api/user/sites?user_uuid=' + self.__user_uuid)

        if response.status_code == 200:
            # Parse JSON reply
            import json
            sites = json.loads(response.text)

            # Find correct site in reply
            for site in sites:
                if site['id_site'] == id_site:
                    return site['site_role']

        return 'Undefined'

    def get_role_for_project(self, id_project: int):
        response = self.do_get_request_to_backend('/api/user/projects?user_uuid=' + self.__user_uuid)

        if response.status_code == 200:
            # Parse JSON reply
            import json
            projects = json.loads(response.text)

            # Find correct site in reply
            for project in projects:
                if project['id_project'] == id_project:
                    return project['project_role']

        return 'Undefined'

    def __repr__(self):
        return '<TeraUserClient - UUID: ' + self.__user_uuid + ', Token: ' + self.__user_token + '>'
