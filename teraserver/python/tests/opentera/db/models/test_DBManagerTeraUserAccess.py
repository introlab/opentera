import unittest
import os

from modules.DatabaseModule.DBManager import DBManager

from opentera.db.models.TeraUser import TeraUser
from opentera.config.ConfigManager import ConfigManager
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class DBManagerTeraUserAccessTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'DBManagerTeraUserAccessTest.db')

    SQLITE = {
        'filename': filename
    }

    def setUp(self):
        super().setUp()
        self.admin_user = TeraUser.get_user_by_username('admin')
        self.test_user = TeraUser.get_user_by_username('user')

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
