from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject


class TeraSessionTypeProjectTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    @staticmethod
    def new_test_session_type_project(id_project: int, id_session_type: int) -> TeraSessionTypeProject:
        st_project = TeraSessionTypeProject()
        st_project.id_project = id_project
        st_project.id_session_type = id_session_type
        TeraSessionTypeProject.insert(st_project)
        return st_project
