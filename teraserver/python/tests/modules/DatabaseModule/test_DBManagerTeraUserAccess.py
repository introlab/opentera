from datetime import datetime, timedelta
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServiceAccess import TeraServiceAccess
from opentera.db.models.TeraUserGroup import TeraUserGroup
from opentera.db.models.TeraTestInvitation import TeraTestInvitation
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess

class DBManagerTeraUserAccessTest(BaseModelsTest):

    def test_admin_get_accessible_users(self):
        with self._flask_app.app_context():
            admin_user = TeraUser.get_user_by_username('admin')
            items = DBManager.userAccess(admin_user).get_accessible_users()
            total_count = TeraUser.get_count()
            self.assertEqual(len(items), total_count)

    def test_no_access_get_accessible_users(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('user4')
            items = DBManager.userAccess(user).get_accessible_users()
            self.assertEqual(len(items), 1)  # Access to self only
            self.assertEqual(items[0].id_user, user.id_user)

    def test_user_get_accessible_users(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('user')
            items = DBManager.userAccess(user).get_accessible_users()
            total_count = len(TeraProject.get_project_by_id(1).get_users_in_project())
            self.assertEqual(len(items), total_count)

    def test_user_get_accessible_users_with_site(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('user')
            items = DBManager.userAccess(user).get_accessible_users(include_site_access=True)
            users = [user.id_user for user in TeraProject.get_project_by_id(1).get_users_in_project()]
            site_access = TeraServiceAccess.get_service_access(
                id_service=TeraService.get_openteraserver_service().id_service, id_site=1)
            for access in site_access:
                users.extend([user.id_user for user in access.service_access_user_group.user_group_users])
            total_count = len(set(users))
            self.assertEqual(len(items), total_count)

    def test_admin_get_accessible_usergroups(self):
        with self._flask_app.app_context():
            admin_user = TeraUser.get_user_by_username('admin')
            items = DBManager.userAccess(admin_user).get_accessible_users_groups()
            total_count = TeraUserGroup.get_count()
            self.assertEqual(len(items), total_count)

    def test_no_access_get_accessible_usergroups(self):
        with self._flask_app.app_context():
            user = TeraUser.get_user_by_username('user4')
            items = DBManager.userAccess(user).get_accessible_users_groups()
            self.assertEqual(len(items), 0)

    # def test_user_get_accessible_usergroups(self):
    #     with self._flask_app.app_context():
    #         user = TeraUser.get_user_by_username('user')
    #         items = DBManager.userAccess(user).get_accessible_users_groups()
    #         total_count = len(TeraProject.get_project_by_id(1).get_users_in_project())
    #         self.assertEqual(len(items), total_count)

    def test_admin_accessible_sites(self):
        with self._flask_app.app_context():
            admin_user = TeraUser.get_user_by_username('admin')
            sites = DBManager.userAccess(admin_user).get_accessible_sites()
            self.assertEqual(len(sites), 2)

    def test_user_accessible_sites(self):
        with self._flask_app.app_context():
            test_user = TeraUser.get_user_by_username('user')
            sites = DBManager.userAccess(test_user).get_accessible_sites()
            self.assertEqual(len(sites), 1)



    def test_get_accessible_tests_invitations_ids(self):
        """
        Testing get_accessible_tests_invitations_ids in different scenarios.
        """
        with self._flask_app.app_context():
            def create_invitation(id_test_type : int,
                                  id_session :int = None,
                                  id_user = None,
                                  id_participant: int = None,
                                  id_device : int = None,
                                  id_project : int = None):
                invitation : TeraTestInvitation = TeraTestInvitation()
                invitation.id_test_type = id_test_type
                invitation.id_session = id_session
                invitation.id_user = id_user
                invitation.id_project = id_project
                invitation.id_participant = id_participant
                invitation.id_device = id_device
                invitation.test_invitation_max_count=1
                invitation.test_invitation_count=0
                invitation.test_invitation_expiration_date = datetime.now() + timedelta(days=1)
                TeraTestInvitation.insert(invitation)
                return invitation

            user = TeraUser.get_user_by_username('admin')

            # Default, there is no invitation in the system
            items = DBManager.userAccess(user).get_accessible_tests_invitations_ids()
            self.assertEqual(len(items), 0)

            # Create invitation for user 1
            invitation1 = create_invitation(1, id_user=1, id_project=1)
            invitation2 = create_invitation(1, id_participant=1, id_project=1)
            invitation3 = create_invitation(1, id_device=1, id_project=1)
            self.assertIsNotNone(invitation1)
            self.assertIsNotNone(invitation2)
            self.assertIsNotNone(invitation3)

            # Admin should see the invitation
            items = DBManager.userAccess(user).get_accessible_tests_invitations_ids()
            self.assertEqual(len(items), 3)

            # Standard user should not see the invitation
            user = TeraUser.get_user_by_username('user4')
            items = DBManager.userAccess(user).get_accessible_tests_invitations_ids()
            self.assertEqual(len(items), 0)
