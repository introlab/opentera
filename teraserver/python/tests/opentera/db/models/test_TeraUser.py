import uuid
import jwt


from modules.DatabaseModule.DBManager import DBManager

from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServiceConfig import TeraServiceConfig
from opentera.db.models.TeraUserUserGroup import TeraUserUserGroup
from opentera.db.models.TeraServiceRole import TeraServiceRole
from opentera.db.models.TeraUserGroup import TeraUserGroup
from opentera.db.models.TeraServiceAccess import TeraServiceAccess

from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from tests.opentera.db.models.test_TeraSession import TeraSessionTest
from tests.opentera.db.models.test_TeraAsset import TeraAssetTest
from tests.opentera.db.models.test_TeraTest import TeraTestTest
from tests.opentera.db.models.test_TeraUserUserGroup import TeraUserUserGroupTest
from tests.opentera.db.models.test_TeraServiceConfig import TeraServiceConfigTest

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
            user = TeraUserTest.new_test_user(user_name="user_soft_delete")
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
            user = TeraUserTest.new_test_user(user_name="user_hard_delete")
            self.assertIsNotNone(user.id_user)
            id_user = user.id_user

            # Assign user to sessions
            user_session = TeraSessionTest.new_test_session(id_creator_user=id_user)
            id_session = user_session.id_session

            user_session = TeraSessionTest.new_test_session(id_creator_service=1, users=[user])
            id_session_invitee = user_session.id_session

            # Attach asset
            asset = TeraAssetTest.new_test_asset(id_session=id_session,
                                                 service_uuid=TeraService.get_openteraserver_service().service_uuid,
                                                 id_user=id_user)
            id_asset = asset.id_asset

            # ... and test
            test = TeraTestTest.new_test_test(id_session=id_session, id_user=id_user)
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

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create new user
            user = TeraUserTest.new_test_user(user_name="user_undelete")
            self.assertIsNotNone(user.id_user)
            id_user = user.id_user

            # Assign to user group
            uug = TeraUserUserGroupTest.new_test_user_usergroup(id_user=id_user, id_user_group=1)
            id_user_user_group = uug.id_user_user_group

            # Assign user to sessions
            user_session = TeraSessionTest.new_test_session(id_creator_user=id_user)
            id_session = user_session.id_session

            user_session = TeraSessionTest.new_test_session(id_creator_service=1, users=[user])
            id_session_invitee = user_session.id_session

            # Attach asset
            asset = TeraAssetTest.new_test_asset(id_session=id_session,
                                                 service_uuid=TeraService.get_openteraserver_service().service_uuid,
                                                 id_user=id_user)
            id_asset = asset.id_asset

            # ... and test
            test = TeraTestTest.new_test_test(id_session=id_session, id_user=id_user)
            id_test = test.id_test

            # ... and service config
            service_conf = TeraServiceConfigTest.new_test_service_config(id_service=1, id_user=id_user)
            id_service_conf = service_conf.id_service_config

            # Soft delete device to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraSession.delete(id_session)
            TeraSession.delete(id_session_invitee)
            TeraUser.delete(id_user)
            self.assertIsNone(TeraUserUserGroup.get_user_user_group_by_id(id_user_user_group))

            # Undelete
            TeraUser.undelete(id_user)

            # Validate
            self.assertIsNotNone(TeraUser.get_user_by_id(id_user))
            self.assertIsNotNone(TeraUserUserGroup.get_user_user_group_by_id(id_user_user_group))
            self.assertIsNone(TeraSession.get_session_by_id(id_session))
            self.assertIsNone(TeraSession.get_session_by_id(id_session_invitee))
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset))
            self.assertIsNone(TeraTest.get_test_by_id(id_test))
            self.assertIsNotNone(TeraServiceConfig.get_service_config_by_id(id_service_conf))

    def test_token_for_admin_should_have_empty_service_access(self):
        with self._flask_app.app_context():
            user = TeraUser()
            user.user_username = 'Test'
            user.user_uuid = str(uuid.uuid4())
            user.user_email = 'test@test.com'
            user.user_firstname = 'Test'
            user.user_lastname = 'Test'
            user.user_password = TeraUser.encrypt_password('test')
            user.user_enabled = True
            user.user_profile = ''
            user.user_notes = ''
            user.user_superadmin = True

            token_key = 'test'

            # Generate token
            token = user.get_token(token_key)
            self.assertIsNotNone(token)

            # Verify token
            token_dict = jwt.decode(token, token_key, algorithms='HS256')
            self.assertIsNotNone(token_dict)

            self.assertTrue('service_access' in token_dict)
            self.assertEqual(token_dict['service_access'], {})  # Should be empty

    def test_token_for_siteadmin_should_have_valid_service_access(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('siteadmin')
            self.assertIsNotNone(user)

            # Create a user group and add user and role to it
            user_group = TeraUserGroup()
            user_group.user_group_name = 'test'
            TeraUserGroup.insert(user_group)

            # Add user to the group
            user_user_group = TeraUserUserGroup()
            user_user_group.id_user = user.id_user
            user_user_group.id_user_group = user_group.id_user_group
            TeraUserUserGroup.insert(user_user_group)

            # Create a role for service
            service = TeraService.get_service_by_key('FileTransferService')
            role = TeraServiceRole()
            role.id_service = service.id_service
            role.service_role_name = 'test'
            TeraServiceRole.insert(role)

            # Create service access
            service_access = TeraServiceAccess()
            service_access.id_service_role = role.id_service_role
            service_access.id_user_group = user_group.id_user_group
            TeraServiceAccess.insert(service_access)

            # Add user to user group
            token_key = 'test'

            # Generate token
            token = user.get_token(token_key)
            self.assertIsNotNone(token)

            # Verify token
            token_dict = jwt.decode(token, token_key, algorithms='HS256')
            self.assertIsNotNone(token_dict)

            # Verify service access
            self.assertTrue('service_access' in token_dict)
            self.assertEqual(token_dict['service_access'], {service.service_key: [role.service_role_name]})

            # TODO delete everything ?
            TeraUserUserGroup.delete(user_user_group.id_user_user_group)
            TeraUserGroup.delete(user_group.id_user_group)
            # TeraServiceAccess.delete(service_access.id_service_access)
            # TeraServiceRole.delete(role.id_service_role)

    def test_disable_2fa_on_2fa_enabled_user_should_reset_secret_email_and_otp_states(self):
        with self._flask_app.app_context():
            user: TeraUser = TeraUserTest.new_test_user(user_name="user_2fa", user_groups=None)
            self.assertIsNotNone(user)
            self.assertFalse(user.user_2fa_enabled)
            # Setup 2FA
            user.enable_2fa_otp()
            self.assertTrue(user.user_2fa_enabled)
            self.assertIsNotNone(user.user_2fa_otp_secret)
            self.assertTrue(user.user_2fa_otp_enabled)
            # Commit user
            self.db.session.add(user)
            self.db.session.commit()
            # Disable 2FA
            user.user_2fa_enabled = False
            self.db.session.add(user)
            self.db.session.commit()
            # Check
            self.assertFalse(user.user_2fa_enabled)
            self.assertIsNone(user.user_2fa_otp_secret)
            self.assertFalse(user.user_2fa_otp_enabled)
            self.assertFalse(user.user_2fa_email_enabled)
            # Delete user
            TeraUser.delete(user.id_user, hard_delete=True)


    def test_change_superadmin_2fa_enabled_while_site_has_2fa_required_does_not_change_2fa_enabled(self):
        with self._flask_app.app_context():
            sites = TeraSite.query.all()
            for site in sites:
                site.site_2fa_required = True
                self.db.session.add(site)
            self.db.session.commit()

            superadmins = TeraUser.query.filter_by(user_superadmin=True).all()
            for superadmin in superadmins:
                self.assertTrue(superadmin.user_2fa_enabled)
                superadmin.user_2fa_enabled = False
                self.db.session.add(superadmin)
            self.db.session.commit()

            # Reverify flag
            for superadmin in superadmins:
                self.assertTrue(superadmin.user_2fa_enabled)

            # Reset site 2fa required
            for site in sites:
                site.site_2fa_required = False
                self.db.session.add(site)
            self.db.session.commit()

            #Reset superadmin 2fa enabled
            for superadmin in superadmins:
                superadmin.user_2fa_enabled = False
                self.db.session.add(superadmin)
            self.db.session.commit()

            for superadmin in superadmins:
                self.assertFalse(superadmin.user_2fa_enabled)

    @staticmethod
    def new_test_user(user_name: str, user_groups: list | None = None) -> TeraUser:
        user = TeraUser()
        user.user_enabled = True
        user.user_firstname = "Test"
        user.user_lastname = "User"
        user.user_profile = ""
        user.user_password = TeraUser.encrypt_password("test")
        user.user_superadmin = False
        user.user_username = user_name
        if user_groups:
            user.user_user_groups = user_groups
        TeraUser.insert(user)
        return user
