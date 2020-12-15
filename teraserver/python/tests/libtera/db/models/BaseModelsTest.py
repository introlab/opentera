import unittest
import os

from modules.DatabaseModule.DBManager import DBManager
from libtera.ConfigManager import ConfigManager
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection


class BaseModelsTest(unittest.TestCase):

    # filename = os.path.join(os.path.dirname(__file__), 'BaseModelsTest.db')
    #
    # SQLITE = {
    #     'filename': filename
    # }
    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        self.admin_user = None
        self.test_user = None

        self.config = ConfigManager()
        self.config.create_defaults()

        self.db_man = DBManager(self.config)

        self.db_man.open_local(self.SQLITE)

        # Creating default users / tests.
        self.db_man.create_defaults(self.config, test=True)

    def tearDown(self):
        pass

    def test_defaults(self):
        pass

    @event.listens_for(Engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, SQLite3Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()