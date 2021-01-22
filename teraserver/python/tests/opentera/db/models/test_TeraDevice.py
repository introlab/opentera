import unittest
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraDevice import TeraDevice
import os
from opentera.config.ConfigManager import ConfigManager
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraDeviceTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'TeraDeviceTest.db')

    SQLITE = {
        'filename': filename
    }

    def test_defaults(self):
        pass

    def test_json(self):
        device = TeraDevice.get_device_by_name('Apple Watch #W05P1')
        json = device.to_json()
        self.assertNotEqual(None, json)
        print(json)
