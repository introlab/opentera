from flask_restx import Resource
from opentera.services.ServiceOpenTera import ServiceOpenTera
from opentera.services.ServiceAccessManager import (current_user_client, current_login_type, current_service_client,
                                                    LoginType)


class EmailResource(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        import services.EmailService.Globals as Globals
        self.module = kwargs.get('flaskModule', None)
        self.service: ServiceOpenTera | None = Globals.service
        self.test = kwargs.get('test', False)

    def _verify_site_access(self, site_id: int, requires_admin: bool = False) -> bool:
        if self.test:
            if current_login_type == LoginType.USER_LOGIN:
                from opentera.db.models.TeraUser import TeraUser
                user: TeraUser | None = TeraUser.get_user_by_uuid(current_user_client.user_uuid)
                if user:
                    roles = user.get_sites_roles()

                    for site in roles:
                        if site.id_site == site_id:
                            if not requires_admin:
                                return True
                            elif roles[site]['site_role'] == 'admin':
                                return True

            if current_login_type == LoginType.SERVICE_LOGIN:
                from opentera.db.models.TeraServiceSite import TeraServiceSite
                from opentera.db.models.TeraService import TeraService
                service = TeraService.get_service_by_uuid(current_service_client.service_uuid)
                sites = TeraServiceSite.get_sites_for_service(service.id_service)
                for site in sites:
                    if site.id_site == site_id:
                        return True
                # params = {'id_site': site_id}
                # response = current_service_client.do_get_request_to_backend("/api/service/sites", params)
                # if response.status_code == 200:
                #     return response.json()
        else:
            user_role_for_site = current_user_client.get_role_for_site(site_id)
            if requires_admin and user_role_for_site == 'admin':
                return True
            elif not requires_admin and user_role_for_site != 'Undefined':
                return True

            if current_login_type == LoginType.SERVICE_LOGIN:
                params = {'id_site': site_id}
                response = current_service_client.do_get_request_to_backend("/api/service/sites", params)
                if response.status_code == 200:
                    return response.json()

        # Anything else return False
        return False

    def _verify_project_access(self, project_id: int, requires_admin: bool = False) -> bool:
        if self.test and self.service:
            if current_login_type == LoginType.USER_LOGIN:
                from opentera.db.models.TeraUser import TeraUser
                user: TeraUser | None = TeraUser.get_user_by_uuid(current_user_client.user_uuid)
                if user:
                    roles = user.get_projects_roles()

                    for proj in roles:
                        if proj.id_project == project_id:
                            if not requires_admin:
                                return True
                            elif roles[proj]['project_role'] == 'admin':
                                return True

            if current_login_type == LoginType.SERVICE_LOGIN:
                from opentera.db.models.TeraServiceProject import TeraServiceProject
                from opentera.db.models.TeraService import TeraService
                service = TeraService.get_service_by_uuid(current_service_client.service_uuid)
                projects = TeraServiceProject.get_projects_for_service(service.id_service)
                for proj in projects:
                    if proj.id_project == project_id:
                        return True
                # params = {'id_project': project_id}
                # response = current_service_client.do_get_request_to_backend("/api/service/projects", params)
                # if response.status_code == 200:
                #     return response.json()
        else:
            if current_login_type == LoginType.USER_LOGIN:
                user_role_for_proj = current_user_client.get_role_for_project(project_id)
                if requires_admin and user_role_for_proj == 'admin':
                    return True
                elif not requires_admin and user_role_for_proj != 'Undefined':
                    return True

            if current_login_type == LoginType.SERVICE_LOGIN:
                params = {'id_project': project_id}
                response = current_service_client.do_get_request_to_backend("/api/service/projects", params)
                if response.status_code == 200:
                    return response.json()

        # Anything else return False
        return False

    def _get_user_infos(self, user_uuid: str) -> str | None:
        response = None
        if current_login_type == LoginType.USER_LOGIN:
            if self.test:
                response = self.service.get_from_opentera('/api/user/users',
                                                             params={'user_uuid': user_uuid},
                                                             token=current_user_client.user_token)
            else:
                response = current_user_client.do_get_request_to_backend('/api/user/users?user_uuid=' + user_uuid)
        if current_login_type == LoginType.SERVICE_LOGIN:
            if self.test:
                if self.test:
                    response = self.service.get_from_opentera('/api/service/users',
                                                              params={'user_uuid': user_uuid},
                                                              token=current_service_client.service_token)
                else:
                    response = current_service_client.do_get_request_to_backend('/api/service/users?user_uuid=' + user_uuid)
        if not response:
            return None
        response_json = response.json()
        if response.status_code == 200 and response_json:
            if isinstance(response_json, list):
                return response_json[0]
            else:
                return response_json

        # If we got here, we don't have access to that user
        return None

    def _get_participant_infos(self, participant_uuid: str) -> str | None:
        response = None
        if current_login_type == LoginType.USER_LOGIN:
            if self.test:
                response = self.service.get_from_opentera('/api/user/participants',
                                                            params={'participant_uuid': participant_uuid},
                                                            token=current_user_client.user_token)
            else:
                response = current_user_client.do_get_request_to_backend('/api/user/participants?participant_uuid=' +
                                                                         participant_uuid)
        if current_login_type == LoginType.SERVICE_LOGIN:
            if self.test:
                response = self.service.get_from_opentera('/api/service/participants',
                                                            params={'participant_uuid': participant_uuid},
                                                            token=current_service_client.service_token)
            else:
                response = current_service_client.do_get_request_to_backend('/api/service/participants?participant_uuid=' +
                                                                         participant_uuid)
        if not response:
            return None
        response_json = response.json()
        if response.status_code == 200 and response_json:
            if isinstance(response_json, list):
                return response_json[0]
            else:
                return response_json

        # If we got here, we don't have access to that participant
        return None