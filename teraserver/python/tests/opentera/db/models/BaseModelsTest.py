import unittest

from opentera.db.Base import db
from modules.DatabaseModule.DBManager import DBManager
from opentera.config.ConfigManager import ConfigManager


class BaseModelsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._config = ConfigManager()
        cls._config.create_defaults()
        cls._db_man = DBManager(cls._config)
        # Setup DB in RAM
        cls._db_man.open_local({}, echo=False, ram=True)

        # Creating default users / tests. Time-consuming, only once per test file.
        cls._db_man.create_defaults(cls._config, test=True)

    @classmethod
    def tearDownClass(cls):
        db.session.remove()

    def setUp(self):
        pass

    def tearDown(self):
        # Make sure pending queries are rollbacked.
        db.session.rollback()

    def test_defaults(self):
        pass

