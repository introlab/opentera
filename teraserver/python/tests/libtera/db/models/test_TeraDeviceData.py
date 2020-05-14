import unittest
from modules.DatabaseModule.DBManager import DBManager
from libtera.db.models.TeraDeviceData import TeraDeviceData
import os
from libtera.ConfigManager import ConfigManager


class TeraDeviceDataTest(unittest.TestCase):

    filename = 'TeraDeviceDataTest.db'

    SQLITE = {
        'filename': filename
    }

    db_man = DBManager()

    config = ConfigManager()

    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        self.db_man.open_local(self.SQLITE)

        # Create default config
        self.config.create_defaults()

        # Creating default users / tests.
        self.db_man.create_defaults(self.config)

    def test_defaults(self):
        pass

    def test_query_filters(self):
        filters = {'id_device': 1,
                   'id_session': 1,
                   'id_device_data': 1}

        val = TeraDeviceData.query_with_filters(filters)
        self.assertEqual(len(val), 1)



