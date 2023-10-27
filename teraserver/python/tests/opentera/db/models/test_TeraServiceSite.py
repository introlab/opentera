from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraServiceSite import TeraServiceSite


class TeraServiceSiteTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    @staticmethod
    def new_test_service_site(id_site: int, id_service: int) -> TeraServiceSite:
        site_service = TeraServiceSite()
        site_service.id_service = id_service
        site_service.id_site = id_site
        TeraServiceSite.insert(site_service)
        return site_service
