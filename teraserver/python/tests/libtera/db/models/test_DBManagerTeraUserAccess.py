import unittest
import os

from modules.DatabaseModule.DBManager import DBManager

from opentera.db.models.TeraUser import TeraUser
from opentera.ConfigManager import ConfigManager


class DBManagerTeraUserAccessTest(unittest.TestCase):

    filename = os.path.join(os.path.dirname(__file__), 'DBManagerTeraUserAccessTest.db')

    SQLITE = {
        'filename': filename
    }

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
        self.db_man.create_defaults(self.config)

        # Load admin user
        self.admin_user = TeraUser.get_user_by_username('admin')

        # Load test user
        self.test_user = TeraUser.get_user_by_username('user')

    def tearDown(self):
        pass

    def test_instance(self):
        self.assertNotEqual(self.admin_user, None)
        self.assertNotEqual(self.test_user, None)

    def test_admin_get_accessible_users_ids(self):
        users = DBManager.userAccess(self.admin_user).get_accessible_users()
        self.assertEqual(len(users), 6)

    def test_admin_accessible_sites(self):
        sites = DBManager.userAccess(self.admin_user).get_accessible_sites()
        self.assertEqual(len(sites), 2)

    def test_admin_accessible_sites(self):
        sites = DBManager.userAccess(self.test_user).get_accessible_sites()
        self.assertEqual(len(sites), 1)
