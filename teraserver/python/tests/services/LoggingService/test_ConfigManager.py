import unittest
from datetime import datetime
from services.LoggingService.ConfigManager import ConfigManager


class LoggingServiceDBManagerTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_defaults(self):
        config = ConfigManager()
        config.create_defaults()
        self.assertTrue(config.validate_config(config.to_dict()))


