from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceType import TeraDeviceType
from sqlalchemy.exc import IntegrityError


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

    def test_insert_invalid_with_device_not_associated_to_project(self):
        with self._flask_app.app_context():
            # Create new device not part of any project or site
            device: TeraDevice = TeraDevice()
            device.device_name = 'Test Device'
            device.device_type = TeraDeviceType.get_device_type_by_key('capteur')
            TeraDevice.insert(device)
            self.assertIsNotNone(device.id_device)

            for participant in TeraParticipant.query.all():
                device_participant: TeraDeviceParticipant = TeraDeviceParticipant()
                device_participant.id_device = device.id_device
                device_participant.id_participant = participant.id_participant
                # Insert should fail since device is not associated with site or project
                self.assertRaises(IntegrityError, TeraDeviceParticipant.insert, device_participant)

            # Delete device
            id_device = device.id_device
            TeraDevice.delete(id_device)

    def test_insert_invalid_with_invalid_participant(self):
        with self._flask_app.app_context():
            # Create new device not part of any project or site
            device: TeraDevice = TeraDevice()
            device.device_name = 'Test Device'
            device.device_type = TeraDeviceType.get_device_type_by_key('capteur')
            TeraDevice.insert(device)
            self.assertIsNotNone(device.id_device)

            device_participant: TeraDeviceParticipant = TeraDeviceParticipant()
            device_participant.id_device = device.id_device
            device_participant.id_participant = None
            # Insert should fail since participant is invalid
            self.assertRaises(IntegrityError, TeraDeviceParticipant.insert, device_participant)

            # Delete device
            id_device = device.id_device
            TeraDevice.delete(id_device)

    def test_insert_invalid_with_invalid_device(self):
        with self._flask_app.app_context():
            for participant in TeraParticipant.query.all():
                device_participant: TeraDeviceParticipant = TeraDeviceParticipant()
                device_participant.id_device = None
                device_participant.id_participant = participant.id_participant
                # Insert should fail since device is invalid
                self.assertRaises(IntegrityError, TeraDeviceParticipant.insert, device_participant)

    def _check_json(self, json_data: dict, with_minimal: bool = True):
        self.assertTrue('id_device_participant' in json_data)
        self.assertTrue('id_device' in json_data)
        self.assertTrue('id_participant' in json_data)
        self.assertFalse('device_participant_device' in json_data)
        self.assertFalse('device_participant_participant' in json_data)

    @staticmethod
    def new_test_device_participant(id_device: int, id_participant: int) -> TeraDeviceParticipant:
        device_part = TeraDeviceParticipant()
        device_part.id_participant = id_participant
        device_part.id_device = id_device
        TeraDeviceParticipant.insert(device_part)
        return device_part
