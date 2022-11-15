import unittest
from modules.DatabaseModule.DBManager import DBManager
from opentera.config.ConfigManager import ConfigManager
from modules.FlaskModule.FlaskModule import flask_app


class BaseModelsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._config = ConfigManager()
        cls._config.create_defaults()
        cls._db_man = DBManager(cls._config)
        # Setup DB in RAM
        cls._db_man.open_local({}, echo=False, ram=True)

        # Creating default users / tests. Time-consuming, only once per test file.
        # with DBManager.app_context():
        with flask_app.app_context():
            cls._db_man.create_defaults(cls._config, test=True)
            cls.db = cls._db_man.db

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass
