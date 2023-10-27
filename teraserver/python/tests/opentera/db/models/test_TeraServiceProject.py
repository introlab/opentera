from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraServiceProject import TeraServiceProject


class TeraServiceProjectTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    @staticmethod
    def new_test_service_project(id_service: int, id_project:int) -> TeraServiceProject:
        service_project = TeraServiceProject()
        service_project.id_service = id_service
        service_project.id_project = id_project
        TeraServiceProject.insert(service_project)
        return service_project
