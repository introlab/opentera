import unittest
import os

from libtera.db.Base import db
from libtera.db.DBManager import DBManager

from libtera.db.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from libtera.db.models.TeraUser import TeraUser


class DBManagerTeraUserAccessTest(unittest.TestCase):

    filename = 'DBManagerTeraUserAccessTest.db'

    SQLITE = {
        'filename': filename
    }

    db_man = DBManager()

    admin_user = None
    test_user = None

    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        self.db_man.open_local(self.SQLITE)
        # Creating default users / tests.
        self.db_man.create_defaults()

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
        access = self.db_man.userAccess(self.admin_user)
        self.assertNotEqual(None, access)
        users = access.get_accessible_users()
        self.assertEqual(len(users), 4)

    def test_admin_accessible_sites(self):
        access = self.db_man.userAccess(self.admin_user)
        self.assertNotEqual(None, access)
        sites = access.get_accessible_sites()
        self.assertEqual(len(sites), 2)

    def test_admin_accessible_sites(self):
        access = self.db_man.userAccess(self.test_user)
        self.assertNotEqual(None, access)

        sites = access.get_accessible_sites()
        self.assertEqual(len(sites), 1)
