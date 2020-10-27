import uuid
from flask import request
from requests import Response


class TeraUserClient:

    def __init__(self, token_dict: dict, token: str, config_man):
        self.__user_uuid = token_dict['user_uuid']
        self.__id_user = token_dict['id_user']
        self.__user_fullname = token_dict['user_fullname']
        self.__user_token = token
        self.__user_superadmin = token_dict['user_superadmin']

        # A little trick here to get the right URL for the server if we are using a proxy
        backend_hostname = config_man.backend_config["hostname"]
        backend_port = str(config_man.backend_config["port"])

        if 'X-Externalhost' in request.headers:
            backend_hostname = request.headers['X-Externalhost']

        if 'X-Externalport' in request.headers:
            backend_port = request.headers['X-Externalport']

        self.__backend_url = 'https://' + backend_hostname + ':' + backend_port

    @property
    def user_uuid(self):
        return self.__user_uuid

    @user_uuid.setter
    def user_uuid(self, u_uuid: uuid):
        self.__user_uuid = u_uuid

    @property
    def id_user(self):
        return self.__id_user

    @id_user.setter
    def id_user(self, id_user: int):
        self.__id_user = id_user

    @property
    def user_fullname(self):
        return self.__user_fullname

    @user_fullname.setter
    def user_fullname(self, name: str):
        self.__user_fullname = name

    @property
    def user_token(self):
        return self.__user_token

    @user_token.setter
    def user_token(self, token: str):
        self.__user_token = token

    @property
    def user_superadmin(self):
        return self.__user_superadmin

    @user_superadmin.setter
    def user_superadmin(self, superadmin: bool):
        self.__user_superadmin = superadmin

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

    def get_user_info(self):
        response = self.do_get_request_to_backend('/api/user/users?user_uuid=' + self.__user_uuid)

        if response.status_code == 200:
            return response.json()

        return {}

    def __repr__(self):
        return '<TeraUserClient - UUID: ' + self.__user_uuid + ', Token: ' + self.__user_token + '>'
