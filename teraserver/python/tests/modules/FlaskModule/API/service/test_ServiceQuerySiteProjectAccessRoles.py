from typing import List

from tests.modules.FlaskModule.API.service.BaseServiceAPITest import BaseServiceAPITest
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraServiceSite import TeraServiceSite

class ServiceQuerySiteProjectAccessRolesTest(BaseServiceAPITest):
    test_endpoint = '/api/service/users/access'

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        with self._flask_app.app_context():
            response = self.test_client.get(self.test_endpoint)
            self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
        with self._flask_app.app_context():
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=None, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_missing_params_site_and_project(self):
        with self._flask_app.app_context():
            user: TeraUser = TeraUser.get_user_by_username('admin')
            params = {
                'uuid_user': user.user_uuid
            }
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_missing_params_uuid_user(self):
        with self._flask_app.app_context():
            params = {
                'id_site': 1
            }
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_and_site_admin(self):
        with self._flask_app.app_context():
            user: TeraUser = TeraUser.get_user_by_username('admin')
            self.assertIsNotNone(user)
            #sites: List[TeraSite] = TeraSite.query.all()
            sites: List[TeraSite] = TeraServiceSite.get_sites_for_service(self.id_service)
            for site in sites:
                params = {
                    'uuid_user': user.user_uuid,
                    'id_site': site.id_site
                }
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(200, response.status_code)
                self.assertEqual({'site_role': 'admin'}, response.json)

    def test_get_endpoint_with_token_auth_and_project_admin(self):
        with self._flask_app.app_context():
            user: TeraUser = TeraUser.get_user_by_username('admin')
            self.assertIsNotNone(user)
            # projects: List[TeraProject] = TeraProject.query.all()
            projects: List[TeraProject] = TeraServiceProject.get_projects_for_service(self.id_service)
            for project in projects:
                params = {
                    'uuid_user': user.user_uuid,
                    'id_project': project.id_project
                }
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(200, response.status_code)
                self.assertEqual({'project_role': 'admin'}, response.json)

    # def test_get_endpoint_with_token_auth_and_project_admin(self):
    #     with self._flask_app.app_context():
    #         # projects: List[TeraProject] = TeraProject.query.all()
    #         projects: List[TeraProject] = TeraServiceProject.get_projects_for_service(self.id_service)
    #         self.assertIsNotNone(projects)
    #         user: TeraUser = TeraUser.get_user_by_username('user')
    #         self.assertIsNotNone(user)
    #         for project in projects:
    #             users = project.service_project_project.get_users_in_project()
    #             if user.id_user not in [p_user.id_user for p_user in users]:
    #                 continue
    #             all_roles = user.get_projects_roles(TeraService.get_openteraserver_service().id_service)
    #             roles = [project_role.project_role for project_role in user.get_projects_roles(self.id_service)
    #                     if project_role.key == project.id_project]
    #             if not roles:
    #                 continue
    #             params = {
    #                 'uuid_user': user.user_uuid,
    #                 'id_project': project.id_project
    #             }
    #             response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
    #                                                          params=params, endpoint=self.test_endpoint)
    #             self.assertEqual(200, response.status_code)
    #             self.assertEqual({'project_role': roles[0]}, response.json)

    def test_get_endpoint_with_token_auth_and_site_siteadmin(self):
        with self._flask_app.app_context():
            user: TeraUser = TeraUser.get_user_by_username('siteadmin')
            self.assertIsNotNone(user)
            sites: List[TeraSite] = TeraSite.query.all()
            from modules.DatabaseModule.DBManager import DBManager
            user_access = DBManager.userAccess(user)
            accessible_sites = user_access.get_accessible_sites_ids()

            for site in sites:
                params = {
                    'uuid_user': user.user_uuid,
                    'id_site': site.id_site
                }
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(200, response.status_code)
                if site.id_site in accessible_sites:
                    self.assertEqual({'site_role': 'admin'}, response.json)
                else:
                    self.assertEqual({'site_role': None}, response.json)

    def test_get_endpoint_with_token_auth_and_project_siteadmin(self):
        with self._flask_app.app_context():
            user: TeraUser = TeraUser.get_user_by_username('siteadmin')
            self.assertIsNotNone(user)
            # projects: List[TeraProject] = TeraProject.query.all()
            projects: List[TeraProject] = TeraServiceProject.get_projects_for_service(self.id_service)

            from modules.DatabaseModule.DBManager import DBManager
            user_access = DBManager.userAccess(user)
            accessible_projects = user_access.get_accessible_projects_ids()

            for project in projects:
                params = {
                    'uuid_user': user.user_uuid,
                    'id_project': project.id_project
                }
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(200, response.status_code)
                if project.id_project in accessible_projects:
                    self.assertEqual({'project_role': 'admin'}, response.json)
                else:
                    self.assertEqual({'project_role': None}, response.json)

    def test_get_endpoint_with_token_auth_and_site_user(self):
        with self._flask_app.app_context():
            user_names = ['user', 'user2', 'user3', 'user4']

            for user_name in user_names:
                user: TeraUser = TeraUser.get_user_by_username(user_name)
                self.assertIsNotNone(user)
                sites: List[TeraSite] = TeraSite.query.all()
                from modules.DatabaseModule.DBManager import DBManager
                user_access = DBManager.userAccess(user)
                accessible_sites = user_access.get_accessible_sites_ids()

                for site in sites:
                    params = {
                        'uuid_user': user.user_uuid,
                        'id_site': site.id_site
                    }
                    response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                                 params=params, endpoint=self.test_endpoint)
                    self.assertEqual(200, response.status_code)
                    if site.id_site in accessible_sites:
                        role = user_access.get_user_site_role(user.id_user, site.id_site)
                        self.assertEqual({'site_role': role['site_role']}, response.json)
                    else:
                        self.assertEqual({'site_role': None}, response.json)

    def test_get_endpoint_with_token_auth_and_project_user(self):
        with self._flask_app.app_context():
            user_names = ['user', 'user2', 'user3', 'user4']

            for user_name in user_names:
                user: TeraUser = TeraUser.get_user_by_username(user_name)
                self.assertIsNotNone(user)
                # projects: List[TeraProject] = TeraProject.query.all()
                projects: List[TeraProject] = TeraServiceProject.get_projects_for_service(self.id_service)

                from modules.DatabaseModule.DBManager import DBManager
                user_access = DBManager.userAccess(user)
                accessible_projects = user_access.get_accessible_projects_ids()

                for project in projects:
                    params = {
                        'uuid_user': user.user_uuid,
                        'id_project': project.id_project
                    }
                    response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                                 params=params, endpoint=self.test_endpoint)
                    self.assertEqual(200, response.status_code)
                    if project.id_project in accessible_projects:
                        role = user_access.get_user_project_role(user.id_user, project.id_project)
                        self.assertEqual({'project_role': role['project_role']}, response.json)
                    else:
                        self.assertEqual({'project_role': None}, response.json)
