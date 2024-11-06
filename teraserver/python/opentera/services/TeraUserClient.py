import uuid
from flask import request
from requests import Response
from typing import List
import json

class TeraUserClient:

    def __init__(self, token_dict: dict, token: str, config_man, service):
        self.__user_uuid = token_dict['user_uuid']
        self.__id_user = token_dict['id_user']
        self.__user_fullname = token_dict['user_fullname']
        self.__user_token = token
        self.__user_superadmin = token_dict['user_superadmin']
        self.__service_access = token_dict['service_access']
        self.__service = service

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

    @property
    def service_access(self):
        return self.__service_access

    @service_access.setter
    def service_access(self, service_access: dict):
        self.__service_access = service_access

    def do_get_request_to_backend(self, path: str, params: dict = None) -> Response:
        """
        Now using service function:
        def get_from_opentera_with_token(self, token: str, api_url: str, params: dict = {},
                                     additional_headers: dict = {}) -> Response:
        """
        if params is None:
            params = {}

        return self.__service.get_from_opentera_with_token(self.__user_token, api_url=path, params=params)

    def get_roles_for_service(self, service_key: str) -> List[str]:
        # Roles are stored in the token, in the service_access dictionary
        roles: List[str] = []

        if service_key in self.__service_access:
            roles = self.__service_access[service_key]
        return roles

    def get_role_for_site(self, id_site: int) -> str:
        params= {'user_uuid': self.__user_uuid}
        response = self.do_get_request_to_backend('/api/user/sites', params)

        if response.status_code == 200:
            # Parse JSON reply
            import json
            sites = json.loads(response.text)

            # Find correct site in reply
            for site in sites:
                if site['id_site'] == id_site:
                    return site['site_role']

        return 'Undefined'

    def get_role_for_project(self, id_project: int) -> str:
        params= {'user_uuid': self.__user_uuid}
        response = self.do_get_request_to_backend('/api/user/projects', params)

        if response.status_code == 200:
            # Parse JSON reply

            projects = json.loads(response.text)

            # Find correct site in reply
            for project in projects:
                if project['id_project'] == id_project:
                    return project['project_role']

        return 'Undefined'

    def get_user_info(self):
        params = {'user_uuid': self.__user_uuid}
        response = self.do_get_request_to_backend('/api/user/users', params)

        if response.status_code == 200:
            return response.json()[0]

        return {}

    def __repr__(self):
        return '<TeraUserClient - UUID: ' + self.__user_uuid + ', Token: ' + self.__user_token + '>'
