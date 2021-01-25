import unittest
import os

from modules.DatabaseModule.DBManager import DBManager

from opentera.config.ConfigManager import ConfigManager
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraDeviceProjectTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'TeraDeviceProjectTest.db')

    SQLITE = {
        'filename': filename
    }

    def test_defaults(self):
        pass
