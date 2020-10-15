import unittest
from modules.DatabaseModule.DBManager import DBManager
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraDeviceType import TeraDeviceType
import os
from libtera.ConfigManager import ConfigManager


class TeraDeviceTest(unittest.TestCase):

    filename = os.path.join(os.path.dirname(__file__), 'TeraDeviceTest.db')

    SQLITE = {
        'filename': filename
    }

    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        # Create default config
        self.config = ConfigManager()
        self.config.create_defaults()
        self.db_man = DBManager(self.config)
        self.db_man.open_local(self.SQLITE)

        # Creating default users / tests.
        self.db_man.create_defaults(self.config)

    def test_defaults(self):
        pass

    def test_json(self):
        device = TeraDevice.get_device_by_name('Apple Watch #W05P1')
        json = device.to_json()
        self.assertNotEqual(None, json)
        print(json)
