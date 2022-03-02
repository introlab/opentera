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
        from modules.FlaskModule.FlaskModule import service_api_ns
        from BaseServiceAPITest import FakeFlaskModule
        # Setup minimal API
        from modules.FlaskModule.API.service.ServiceQuerySites import ServiceQuerySites
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseServiceAPITest.getConfig())}
        service_api_ns.add_resource(ServiceQuerySites, '/sites', resource_class_kwargs=kwargs)

        # Setup token
        self.setup_service_token()

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_get_endpoint_no_auth(self):
        response = self.test_client.get(self.test_endpoint)
        self.assertEqual(401, response.status_code)

    def test_get_endpoint_with_token_auth_no_params(self):
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
        params = {'invalid_param': True}
        response = self._get_with_service_token_auth(client=self.test_client, token=self.service_token,
                                                     params=params, endpoint=self.test_endpoint)
        self.assertEqual(400, response.status_code)



# get_parser.add_argument('id_site', type=int, help='ID of the site to query')
# get_parser.add_argument('id_user', type=int, help='ID of the user to query sites for')