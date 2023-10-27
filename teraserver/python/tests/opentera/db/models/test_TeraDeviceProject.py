from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraDeviceProject import TeraDeviceProject
from opentera.db.models.TeraDeviceSite import TeraDeviceSite
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraDeviceType import TeraDeviceType
from sqlalchemy.exc import IntegrityError


class TeraDeviceProjectTest(BaseModelsTest):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_defaults(self):
        with self._flask_app.app_context():
            device_projects = TeraDeviceProject.query.all()
            self.assertGreater(len(device_projects), 0)

            for device_project in device_projects:
                for minimal in [True, False]:
                    json_data = device_project.to_json(minimal=minimal)
                    self.assertGreater(len(json_data), 0)
                    self._check_json(json_data, with_minimal=minimal)

    def test_insert_invalid_with_device_not_associated_to_site(self):
        with self._flask_app.app_context():
            # Create new device not part of any project or site
            device: TeraDevice = TeraDevice()
            device.device_name = 'Test Device'
            device.device_type = TeraDeviceType.get_device_type_by_key('capteur')
            TeraDevice.insert(device)
            self.assertIsNotNone(device.id_device)

            for project in TeraProject.query.all():
                device_project: TeraDeviceProject = TeraDeviceProject()
                device_project.id_device = device.id_device
                device_project.id_project = project.id_project

                # Insert should fail since device is not associated with site or project
                self.assertRaises(IntegrityError, TeraDeviceProject.insert, device_project)

            # Delete device
            id_device = device.id_device
            TeraDevice.delete(id_device)

    def test_insert_invalid_with_invalid_project(self):
        with self._flask_app.app_context():
            # Create new device not part of any project or site
            device: TeraDevice = TeraDevice()
            device.device_name = 'Test Device'
            device.device_type = TeraDeviceType.get_device_type_by_key('capteur')
            TeraDevice.insert(device)
            self.assertIsNotNone(device.id_device)

            device_project: TeraDeviceProject = TeraDeviceProject()
            device_project.id_device = device.id_device
            device_project.id_project = None
            self.assertRaises(IntegrityError, TeraDeviceProject.insert, device_project)

            # Delete device
            id_device = device.id_device
            TeraDevice.delete(id_device)

    def test_insert_invalid_with_invalid_device(self):
        with self._flask_app.app_context():
            for project in TeraProject.query.all():
                device_project: TeraDeviceProject = TeraDeviceProject()
                device_project.id_device = None
                device_project.id_project = project.id_project
                self.assertRaises(IntegrityError, TeraDeviceProject.insert, device_project)

    def test_insert_with_device_associated_to_site(self):
        with self._flask_app.app_context():
            # Create new device not part of any project or site
            device: TeraDevice = TeraDevice()
            device.device_name = 'Test Device'
            device.device_type = TeraDeviceType.get_device_type_by_key('capteur')
            TeraDevice.insert(device)
            self.assertIsNotNone(device.id_device)

            # Associate with every site
            for site in TeraSite.query.all():
                device_site: TeraDeviceSite = TeraDeviceSite()
                device_site.id_device = device.id_device
                device_site.id_site = site.id_site
                TeraDeviceSite.insert(device_site)
                self.assertIsNotNone(device_site.id_device_site)

                # Get project for this site
                for project in site.site_projects:
                    device_project: TeraDeviceProject = TeraDeviceProject()
                    device_project.id_device = device.id_device
                    device_project.id_project = project.id_project
                    TeraDeviceProject.insert(device_project)
                    self.assertIsNotNone(device_project.id_device_project)

                    # delete it
                    id_device_project = device_project.id_device_project
                    TeraDeviceProject.delete(id_device_project)
                    self.assertIsNone(TeraDeviceProject.get_device_project_by_id(id_device_project))

                # Delete device_site
                id_device_site = device_site.id_device_site
                TeraDeviceSite.delete(id_device_site)
                self.assertIsNone(TeraDeviceSite.get_device_site_by_id(id_device_site))

            # Delete device
            id_device = device.id_device
            TeraDevice.delete(id_device)

    def _check_json(self, json_data: dict, with_minimal: bool = True):
        self.assertTrue('id_device_project' in json_data)
        self.assertTrue('id_device' in json_data)
        self.assertTrue('id_project' in json_data)
        self.assertFalse('device_project_device' in json_data)
        self.assertFalse('device_project_project' in json_data)

    @staticmethod
    def new_test_device_project(id_device: int, id_project: int) -> TeraDeviceProject:
        device_project = TeraDeviceProject()
        device_project.id_project = id_project
        device_project.id_device = id_device
        TeraDeviceProject.insert(device_project)
        return device_project
