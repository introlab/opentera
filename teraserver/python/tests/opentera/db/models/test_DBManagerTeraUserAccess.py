from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraUser import TeraUser
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from modules.FlaskModule.FlaskModule import flask_app


class DBManagerTeraUserAccessTest(BaseModelsTest):

    def setUp(self):
        super().setUp()

    def test_admin_get_accessible_users_ids(self):
        with flask_app.app_context():
            admin_user = TeraUser.get_user_by_username('admin')
            users = DBManager.userAccess(admin_user).get_accessible_users()
            self.assertEqual(len(users), 6)

    def test_admin_accessible_sites(self):
        with flask_app.app_context():
            admin_user = TeraUser.get_user_by_username('admin')
            sites = DBManager.userAccess(admin_user).get_accessible_sites()
            self.assertEqual(len(sites), 2)

    def test_user_accessible_sites(self):
        with flask_app.app_context():
            test_user = TeraUser.get_user_by_username('user')
            sites = DBManager.userAccess(test_user).get_accessible_sites()
            self.assertEqual(len(sites), 1)
