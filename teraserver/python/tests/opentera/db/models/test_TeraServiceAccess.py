from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraServiceAccess import TeraServiceAccess


class TeraServiceAccessTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    @staticmethod
    def new_test_service_access(id_service_role: int, id_user_group: int | None = None,
                                id_participant_group: int | None = None,
                                id_device: int | None = None) -> TeraServiceAccess:
        access = TeraServiceAccess()
        access.id_service_role = id_service_role
        if id_user_group:
            access.id_user_group = id_user_group
        if id_participant_group:
            access.id_participant_group = id_participant_group
        if id_device:
            access.id_device = id_device
        TeraServiceAccess.insert(access)
        return access
