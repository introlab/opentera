from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraServiceConfig import TeraServiceConfig


class TeraServiceConfigTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    @staticmethod
    def new_test_service_config(id_service: int, id_device: int | None = None, id_participant: int | None = None,
                                id_user: int | None = None, config: str = "{}"):
        device_service_config = TeraServiceConfig()
        if id_device:
            device_service_config.id_device = id_device
        if id_participant:
            device_service_config.id_participant = id_participant
        if id_user:
            device_service_config.id_user = id_user
        device_service_config.id_service = id_service
        device_service_config.service_config_config = config
        TeraServiceConfig.insert(device_service_config)
        return device_service_config
