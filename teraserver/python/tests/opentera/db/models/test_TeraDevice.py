from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceType import TeraDeviceType
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraDeviceTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            devices = TeraDevice.query.all()
            self.assertGreater(len(devices), 0)

    def test_json_full_and_minimal(self):
        with self._flask_app.app_context():
            devices = TeraDevice.query.all()
            self.assertGreater(len(devices), 0)
            for minimal in [False, True]:
                for device in devices:
                    self.assertIsNotNone(device)
                    json = device.to_json(minimal=minimal)
                    self.assertNotEqual(None, json)

                    if not minimal:
                        # Full fields only
                        self.assertTrue('device_config' in json)
                        self.assertTrue('device_infos' in json)
                        self.assertTrue('device_lastonline' in json)
                        self.assertTrue('device_notes' in json)
                        self.assertTrue('device_onlineable' in json)
                        self.assertTrue('device_token' in json)

                    # Minimal + full fields
                    self.assertTrue('device_enabled' in json)
                    self.assertTrue('device_name' in json)
                    self.assertTrue('device_uuid' in json)
                    self.assertTrue('id_device' in json)
                    self.assertTrue('id_device_type' in json)
                    self.assertTrue('id_device_subtype' in json)

                    # Make sure deleted at field not there
                    self.assertFalse('deleted_at' in json)

    def test_insert_with_minimal_config(self):
        with self._flask_app.app_context():
            # Create a new device
            device = TeraDevice()
            device.device_name = 'Test device'
            device.id_device_type = TeraDeviceType.get_device_type_by_key('capteur').id_device_type
            TeraDevice.insert(device)
            self.assertIsNotNone(device.id_device)
            self.assertIsNotNone(device.device_token)
            self.assertIsNotNone(device.device_uuid)
            self.assertFalse(device.device_enabled)
            self.assertFalse(device.device_onlineable)
            self.assertIsNone(device.device_config)
            self.assertIsNone(device.device_infos)
            self.assertIsNone(device.device_lastonline)
            self.assertIsNone(device.device_notes)

            # Destroy device
            TeraDevice.delete(device.id_device)

    def test_update(self):
        with self._flask_app.app_context():
            device: TeraDevice = TeraDevice.get_device_by_id(1)
            self.assertIsNotNone(device)
            update_info = {'device_notes': 'Test notes'}
            # device.device_notes = 'Test notes'
            TeraDevice.update(device.id_device, update_info)
            # TeraDevice.update(device.id_device, device.to_json(minimal=True))
            device = TeraDevice.get_device_by_id(1)
            self.assertIsNotNone(device)
            self.assertEqual('Test notes', device.device_notes)

    def test_delete(self):
        with self._flask_app.app_context():
            # Create a new device
            device = TeraDevice()
            device.device_name = 'Test device'
            device.id_device_type = TeraDeviceType.get_device_type_by_key('capteur').id_device_type
            TeraDevice.insert(device)
            self.assertIsNotNone(device.id_device)
            id_device = device.id_device
            # Delete device
            TeraDevice.delete(device.id_device)
            # Make sure device is deleted
            # Warning, device was deleted, device object is not valid anymore
            self.assertIsNone(TeraDevice.get_device_by_id(id_device))

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create a new device
            device = TeraDevice()
            device.device_name = 'Test device'
            device.id_device_type = TeraDeviceType.get_device_type_by_key('capteur').id_device_type
            TeraDevice.insert(device)
            self.assertIsNotNone(device.id_device)
            id_device = device.id_device
            # Delete device
            TeraDevice.delete(device.id_device)
            # Make sure device is deleted
            # Warning, device was deleted, device object is not valid anymore
            self.assertIsNone(TeraDevice.get_device_by_id(id_device))

            # Query device, with soft delete flag
            device = TeraDevice.query.filter_by(id_device=id_device).execution_options(include_deleted=True).first()
            self.assertIsNotNone(device)
            self.assertIsNotNone(device.deleted_at)


