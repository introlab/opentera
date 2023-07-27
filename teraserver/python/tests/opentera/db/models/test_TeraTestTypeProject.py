from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject


class TeraTestTypeProjectTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    @staticmethod
    def new_test_test_type_project(id_project: int, id_test_type: int) -> TeraTestTypeProject:
        tt_project = TeraTestTypeProject()
        tt_project.id_project = id_project
        tt_project.id_test_type = id_test_type
        TeraTestTypeProject.insert(tt_project)
        return tt_project
