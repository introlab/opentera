from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant


class TeraDeviceParticipantTest(BaseModelsTest):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_defaults(self):
        with self._flask_app.app_context():
            device_participants = TeraDeviceParticipant.query.all()
            self.assertGreater(len(device_participants), 0)

            for device_participant in device_participants:
                for minimal in [True, False]:
                    json_data = device_participant.to_json(minimal=minimal)
                    self.assertGreater(len(json_data), 0)
                    self._check_json(json_data, with_minimal=minimal)

    def _check_json(self, json_data: dict, with_minimal: bool = True):
        self.assertTrue('id_device_participant' in json_data)
        self.assertTrue('id_device' in json_data)
        self.assertTrue('id_participant' in json_data)
        self.assertFalse('device_participant_device' in json_data)
        self.assertFalse('device_participant_participant' in json_data)
