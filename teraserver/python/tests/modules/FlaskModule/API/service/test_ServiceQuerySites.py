from typing import List

from BaseServiceAPITest import BaseServiceAPITest
from modules.FlaskModule.FlaskModule import flask_app
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraService import TeraService


class ServiceQuerySitesTest(BaseServiceAPITest):
    test_endpoint = '/api/service/sites'

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
            self.assertEqual(200, response.status_code)
            service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
            from modules.DatabaseModule.DBManager import DBManager
            service_access = DBManager.serviceAccess(service)
            accessible_sites = service_access.get_accessibles_sites_ids()
            for site_json in response.json:
                id_site = site_json['id_site']
                if id_site in accessible_sites:
                    site: TeraSite = TeraSite.get_site_by_id(id_site)
                    self.assertEqual(site.to_json(minimal=True), site_json)

    def test_get_endpoint_with_token_auth_and_invalid_params(self):
        with self._flask_app.app_context():
            params = {'invalid_param': True}
            response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                         params=params, endpoint=self.test_endpoint)
            self.assertEqual(400, response.status_code)

    def test_get_endpoint_with_token_auth_and_id_site(self):
        with self._flask_app.app_context():
            sites: List[TeraSite] = TeraSite.query.all()
            for site in sites:
                service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
                from modules.DatabaseModule.DBManager import DBManager
                service_access = DBManager.serviceAccess(service)
                accessible_sites = service_access.get_accessibles_sites_ids()

                params = {'id_site': site.id_site}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)

                if site.id_site in accessible_sites:
                    self.assertEqual(200, response.status_code)
                    for site_json in response.json:
                        id_site = site_json['id_site']
                        self.assertEqual(site.id_site, id_site)
                        self.assertEqual(site.to_json(minimal=True), site_json)
                else:
                    self.assertEqual(403, response.status_code)

    def test_get_endpoint_with_token_auth_and_id_site(self):
        with self._flask_app.app_context():
            users: List[TeraUser] = TeraUser.query.all()
            for user in users:
                service: TeraService = TeraService.get_service_by_uuid(self.service_uuid)
                from modules.DatabaseModule.DBManager import DBManager
                service_access = DBManager.serviceAccess(service)
                accessible_sites = service_access.get_accessibles_sites_ids()

                params = {'id_user': user.id_user}
                response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                             params=params, endpoint=self.test_endpoint)
                self.assertEqual(200, response.status_code)

                for site_json in response.json:
                    id_site = site_json['id_site']
                    site: TeraSite = TeraSite.get_site_by_id(id_site)
                    self.assertEqual(site.id_site, id_site)
                    self.assertTrue(id_site in accessible_sites)
                    self.assertEqual(site.to_json(minimal=True), site_json)
