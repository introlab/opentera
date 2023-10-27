from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite


class TeraSessionTypeSiteTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    @staticmethod
    def new_test_session_type_site(id_site: int, id_session_type: int) -> TeraSessionTypeSite:
        st_site = TeraSessionTypeSite()
        st_site.id_site = id_site
        st_site.id_session_type = id_session_type
        TeraSessionTypeSite.insert(st_site)
        return st_site
