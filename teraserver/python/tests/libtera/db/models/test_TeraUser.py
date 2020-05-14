import unittest
from modules.DatabaseModule.DBManager import DBManager
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
import os
from libtera.ConfigManager import ConfigManager


class TeraUserTest(unittest.TestCase):

    filename = 'TeraUserTest.db'

    SQLITE = {
        'filename': filename
    }

    db_man = DBManager()

    config = ConfigManager()

    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        self.db_man.open_local(self.SQLITE)

        # Create default config
        self.config.create_defaults()

        # Creating default users / tests.
        self.db_man.create_defaults(self.config)

    def tearDown(self):
        pass

    def test_empty(self):
        pass

    def test_superadmin(self):
        # Superadmin should have access to everything.
        admin = TeraUser.get_user_by_username('admin')
        self.assertNotEqual(admin, None, 'admin user not None')
        self.assertEqual(True, isinstance(admin, TeraUser), 'admin user is a TeraUser')
        self.assertTrue(admin.user_superadmin, 'admin user is superadmin')
        self.assertTrue(TeraUser.verify_password('admin', 'admin'), 'admin user default password is admin')

        # Verify that superadmin can access all sites
        sites = DBManager.userAccess(admin).get_accessible_sites()
        self.assertEqual(len(sites), TeraSite.get_count(), 'admin user can access all sites')

        # Verify that superadmin can access all projects
        projects = DBManager.userAccess(admin).get_accessible_projects()
        self.assertEqual(len(projects), TeraProject.get_count())

    def test_siteadmin(self):
        # Site admin should have access to the site
        siteadmin = TeraUser.get_user_by_username('siteadmin')
        self.assertNotEqual(siteadmin, None, 'siteadmin user not None')
        self.assertEqual(True, isinstance(siteadmin, TeraUser), 'siteadmin user is a TeraUser')
        self.assertFalse(siteadmin.user_superadmin, 'siteadmin user is not superadmin')
        self.assertTrue(TeraUser.verify_password('siteadmin', 'siteadmin'),
                        'siteadmin user default password is admin')

        # Verify that site can access only its site
        sites = DBManager.userAccess(siteadmin).get_accessible_sites()
        self.assertEqual(len(sites), 1, 'siteadmin user can access 1 site')
        self.assertEqual(sites[0].site_name, 'Default Site')

        # Verify that siteadmin can access all sites project
        projects = DBManager.userAccess(siteadmin).get_accessible_projects()
        self.assertEqual(len(projects), 2)

    def test_multisite_user(self):
        multi = TeraUser.get_user_by_username('user2')
        self.assertNotEqual(multi, None, 'user2 user not None')
        self.assertEqual(True, isinstance(multi, TeraUser), 'user2 user is a TeraUser')
        self.assertFalse(multi.user_superadmin, 'user2 user is not superadmin')
        self.assertTrue(TeraUser.verify_password('user2', 'user2'),
                        'user2 user default password is user2')

        # Verify that site can access only its site
        sites = DBManager.userAccess(multi).get_accessible_sites()
        self.assertEqual(len(sites), 1, 'multi user can access 1 site')
        self.assertEqual(sites[0].site_name, 'Default Site')

        # Verify that multi can access 2 projects
        projects = DBManager.userAccess(multi).get_accessible_projects()
        self.assertEqual(len(projects), 2)
