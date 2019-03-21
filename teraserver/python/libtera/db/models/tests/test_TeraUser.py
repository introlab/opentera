import unittest
from libtera.db.DBManager import DBManager
import os


class TeraUserTest(unittest.TestCase):

    filename = 'TeraUserTest.db'

    SQLITE = {
        'filename': filename
    }

    db = DBManager()

    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        self.db.open_local(self.SQLITE)
        self.db.create_defaults()

    def tearDown(self):
        pass

    def test_hello(self):
        pass

