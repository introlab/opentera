import unittest
from modules.DatabaseModule.DBManager import DBManager
from opentera.config.ConfigManager import ConfigManager
from flask import Flask


class BaseModelsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._config = ConfigManager()
        cls._config.create_defaults()
        cls._flask_app = Flask('BaseModelsTest')
        cls._flask_app.debug = False
        cls._flask_app.testing = True
        cls._db_man = DBManager(cls._config, app=cls._flask_app)
        # Setup DB in RAM
        cls._db_man.open_local({}, echo=False, ram=True)

        # Creating default users / tests. Time-consuming, only once per test file.
        with cls._flask_app.app_context():
            cls._db_man.create_defaults(cls._config, test=True)
            cls.db = cls._db_man.db

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass
