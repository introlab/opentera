from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraDeviceSite import TeraDeviceSite
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDeviceProject import TeraDeviceProject
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraDeviceType import TeraDeviceType
from sqlalchemy.exc import IntegrityError


class TeraDeviceSiteTest(BaseModelsTest):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_defaults(self):
        with self._flask_app.app_context():
            device_sites = TeraDeviceSite.query.all()
            self.assertGreater(len(device_sites), 0)

            for device_site in device_sites:
                for minimal in [True, False]:
                    json_data = device_site.to_json(minimal=minimal)
                    self.assertGreater(len(json_data), 0)
                    self._check_json(json_data, with_minimal=minimal)

    def test_insert_and_delete_with_no_associated_project(self):
        with self._flask_app.app_context():
            # Create a Device and add it to every site
            device: TeraDevice = TeraDevice()
            device.device_name = 'Test Device'
            device.device_type = TeraDeviceType.get_device_type_by_key('capteur')
            TeraDevice.insert(device)
            self.assertIsNotNone(device.id_device)
            id_device = device.id_device

            for site in TeraSite.query.all():
                device_site: TeraDeviceSite = TeraDeviceSite()
                device_site.id_device = device.id_device
                device_site.id_site = site.id_site
                TeraDeviceSite.insert(device_site)
                self.assertIsNotNone(device_site.id_device_site)
                id_device_site = device_site.id_device_site
                # Immediate delete of device_site
                TeraDeviceSite.delete(device_site.id_device_site, autocommit=True)
                self.assertIsNone(TeraDeviceSite.get_device_site_by_id(id_device_site))

            TeraDevice.delete(device.id_device)
            self.assertIsNone(TeraDevice.get_device_by_id(id_device))

    def test_insert_and_delete_with_associated_project_and_no_participant(self):
        with self._flask_app.app_context():
            # Create a Device and add it to every site
            device: TeraDevice = TeraDevice()
            device.device_name = 'Test Device'
            device.device_type = TeraDeviceType.get_device_type_by_key('capteur')
            TeraDevice.insert(device)
            self.assertIsNotNone(device.id_device)

            for site in TeraSite.query.all():
                device_site: TeraDeviceSite = TeraDeviceSite()
                device_site.id_device = device.id_device
                device_site.id_site = site.id_site
                TeraDeviceSite.insert(device_site)
                self.assertIsNotNone(device_site.id_device_site)
                id_device_site = device_site.id_device_site

                # Create a project in the site with this device
                project: TeraProject = TeraProject()
                project.project_name = 'Test Project'
                project.project_site = site
                project.project_devices = [device]
                TeraProject.insert(project)
                self.assertIsNotNone(project.id_project)

                # Make sure the device and site are associated
                self.assertIsNotNone(TeraDeviceProject.get_device_project_id_for_device_and_project(
                    device_id=device.id_device, project_id=project.id_project))

                # Then delete the device_site
                TeraDeviceSite.delete(device_site.id_device_site, autocommit=True)
                self.assertIsNone(TeraDeviceSite.get_device_site_by_id(id_device_site))

            id_device = device.id_device
            TeraDevice.delete(device.id_device)
            self.assertIsNone(TeraDevice.get_device_by_id(id_device))

    def test_insert_and_delete_with_associated_project_and_no_participant(self):
        with self._flask_app.app_context():
            # Create a Device and add it to every site
            device: TeraDevice = TeraDevice()
            device.device_name = 'Test Device'
            device.device_type = TeraDeviceType.get_device_type_by_key('capteur')
            TeraDevice.insert(device)
            self.assertIsNotNone(device.id_device)

            for site in TeraSite.query.all():
                device_site: TeraDeviceSite = TeraDeviceSite()
                device_site.id_device = device.id_device
                device_site.id_site = site.id_site
                TeraDeviceSite.insert(device_site)
                self.assertIsNotNone(device_site.id_device_site)
                id_device_site = device_site.id_device_site

                # Create a project in the site with this device
                project: TeraProject = TeraProject()
                project.project_name = 'Test Project'
                project.project_site = site
                project.project_devices = [device]
                TeraProject.insert(project)
                self.assertIsNotNone(project.id_project)

                # Create a participant in this project
                participant: TeraParticipant = TeraParticipant()
                participant.participant_name = "Test"
                participant.participant_enabled = True
                participant.participant_project = project
                participant.participant_devices = [device]
                TeraParticipant.insert(participant)
                self.assertIsNotNone(participant.id_participant)

                # Make sure the device and project are associated
                self.assertIsNotNone(TeraDeviceProject.get_device_project_id_for_device_and_project(
                    device_id=device.id_device, project_id=project.id_project))

                # Make sure the device and participant are associated
                dp: TeraDeviceParticipant = TeraDeviceParticipant()
                dp.id_device = device.id_device
                dp.id_participant = participant.id_participant
                TeraDeviceParticipant.insert(dp)

                # Then delete the device_site
                self.assertRaises(IntegrityError, TeraDeviceSite.delete, device_site.id_device_site, autocommit=True)
                TeraDeviceParticipant.delete(dp.id_device_participant)
                TeraDeviceSite.delete(device_site.id_device_site)
                self.assertIsNone(TeraDeviceSite.get_device_site_by_id(id_device_site))

                # Check for auto-deletion of device-project
                self.assertIsNone(TeraDeviceProject.get_device_project_id_for_device_and_project(device.id_device,
                                                                                                 project.id_project))

            id_device = device.id_device
            TeraDevice.delete(device.id_device)
            self.assertIsNone(TeraDevice.get_device_by_id(id_device))

    def _check_json(self, json_data: dict, with_minimal: bool = True):
        self.assertTrue('id_device_site' in json_data)
        self.assertTrue('id_device' in json_data)
        self.assertTrue('id_site' in json_data)
        self.assertFalse('device_site_site' in json_data)
        self.assertFalse('device_site_device' in json_data)

