import unittest
import os

from modules.DatabaseModule.DBManager import DBManager

from opentera.config.ConfigManager import ConfigManager
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraServiceProjectTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'TeraServiceProjectTest.db')

    SQLITE = {
        'filename': filename
    }

    def test_defaults(self):
        pass
