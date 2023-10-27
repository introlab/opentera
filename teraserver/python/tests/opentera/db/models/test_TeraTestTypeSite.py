from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite


class TeraTestTypeSiteTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    @staticmethod
    def new_test_test_type_site(id_site: int, id_test_type: int) -> TeraTestTypeSite:
        tt_site = TeraTestTypeSite()
        tt_site.id_site = id_site
        tt_site.id_test_type = id_test_type
        TeraTestTypeSite.insert(tt_site)
        return tt_site
