from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraService import TeraService
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraUserTest(BaseModelsTest):

    def test_empty(self):
        with self._flask_app.app_context():
            pass

    def test_superadmin(self):
        with self._flask_app.app_context():
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
        with self._flask_app.app_context():
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
        with self._flask_app.app_context():
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

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            user = TeraUser()
            user.user_enabled = True
            user.user_firstname = "Test"
            user.user_lastname = "User"
            user.user_profile = ""
            user.user_password = TeraUser.encrypt_password("test")
            user.user_superadmin = False
            user.user_username = "test"
            TeraUser.insert(user)
            self.assertIsNotNone(user.id_user)
            id_user = user.id_user

            # Soft delete
            TeraUser.delete(id_user)
            # Make sure participant is deleted
            self.assertIsNone(TeraUser.get_user_by_id(id_user))

            # Query, with soft delete flag
            user = TeraUser.query.filter_by(id_user=id_user).execution_options(include_deleted=True).first()
            self.assertIsNotNone(user)
            self.assertIsNotNone(user.deleted_at)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create new user
            user = TeraUser()
            user.user_enabled = True
            user.user_firstname = "Test"
            user.user_lastname = "User"
            user.user_profile = ""
            user.user_password = TeraUser.encrypt_password("test")
            user.user_superadmin = False
            user.user_username = "test"
            TeraUser.insert(user)
            self.assertIsNotNone(user.id_user)
            id_user = user.id_user

            # Assign user to sessions
            user_session = TeraSession()
            user_session.id_creator_user = id_user
            user_session.id_session_type = 1
            user_session.session_name = 'Creator user session'
            TeraSession.insert(user_session)
            id_session = user_session.id_session

            user_session = TeraSession()
            user_session.id_creator_service = 1
            user_session.id_session_type = 1
            user_session.session_name = "User invitee session"
            user_session.session_users = [user]
            TeraSession.insert(user_session)
            id_session_invitee = user_session.id_session

            # Attach asset
            asset = TeraAsset()
            asset.asset_name = "User asset test"
            asset.id_user = id_user
            asset.id_session = id_session
            asset.asset_service_uuid = TeraService.get_openteraserver_service().service_uuid
            asset.asset_type = 'Test'
            TeraAsset.insert(asset)
            id_asset = asset.id_asset

            # ... and test
            test = TeraTest()
            test.id_user = id_user
            test.id_session = id_session
            test.id_test_type = 1
            test.test_name = "User test test!"
            TeraTest.insert(test)
            id_test = test.id_test

            # Soft delete device to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraSession.delete(id_session)
            TeraSession.delete(id_session_invitee)
            TeraUser.delete(id_user)

            # Check that relationships are still there
            self.assertIsNone(TeraUser.get_user_by_id(id_user))
            self.assertIsNotNone(TeraUser.get_user_by_id(id_user, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session))
            self.assertIsNotNone(TeraSession.get_session_by_id(id_session, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session_invitee))
            self.assertIsNotNone(TeraSession.get_session_by_id(id_session_invitee, True))
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset))
            self.assertIsNotNone(TeraAsset.get_asset_by_id(id_asset, True))
            self.assertIsNone(TeraTest.get_test_by_id(id_test))
            self.assertIsNotNone(TeraTest.get_test_by_id(id_test, True))

            # Hard delete participant
            TeraUser.delete(user.id_user, hard_delete=True)

            # Make sure device and associations are deleted
            self.assertIsNone(TeraUser.get_user_by_id(id_user, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session_invitee, True))
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset, True))
            self.assertIsNone(TeraTest.get_test_by_id(id_test, True))
