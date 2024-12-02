from datetime import datetime, timezone, timedelta

from sqlalchemy.exc import IntegrityError

from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraTestInvitation import TeraTestInvitation


class TeraTestInvitationTest(BaseModelsTest):
    """
    Test TeraTestInvitation database model.
    """

    def test_defaults(self):
        """
        Test default values at object creation
        """
        with self._flask_app.app_context():
            pass

    def test_db_events_not_none(self):
        """
        Test that db events are not None
        """
        with self._flask_app.app_context():
            invitation : TeraTestInvitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_user=1)
            self.assertIsNotNone(invitation.to_json_create_event())
            self.assertIsNotNone(invitation.to_json_update_event())
            self.assertIsNotNone(invitation.to_json_delete_event())

    def test_create_with_no_user_participant_device(self):
        """
        Test creating an invitation with no user, participant or device will raise an IntegrityError.
        """
        with self._flask_app.app_context():
            with self.assertRaises(IntegrityError):
                TeraTestInvitationTest.new_test_invitation(id_test_type=1)

    def test_create_with_user_and_participant(self):
        """
        Test creating an invitation with both user and participant will raise an IntegrityError.
        """
        with self._flask_app.app_context():
            with self.assertRaises(IntegrityError):
                TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_user=1, id_participant=1)

    def test_create_with_user_and_device(self):
        """
        Test creating an invitation with both user and device will raise an IntegrityError.
        """
        with self._flask_app.app_context():
            with self.assertRaises(IntegrityError):
                TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_user=1, id_device=1)

    def test_create_with_invalid_test_type(self):
        """
        Test creating an invitation with an invalid test type will raise an IntegrityError.
        """
        with self._flask_app.app_context():
            with self.assertRaises(IntegrityError):
                TeraTestInvitationTest.new_test_invitation(id_test_type=9999)

    def test_create_with_invalid_session_type(self):
        """
        Test creating an invitation with an invalid session type will raise an IntegrityError.
        """
        with self._flask_app.app_context():
            with self.assertRaises(IntegrityError):
                TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_session=9999)

    def test_create_with_invalid_user(self):
        """
        Test creating an invitation with an invalid user will raise an IntegrityError.
        """
        with self._flask_app.app_context():
            with self.assertRaises(IntegrityError):
                TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_user=9999)

    def test_create_with_valid_test_type_and_user(self):
        """
        Test creating an invitation with a valid test type and user.
        """
        with self._flask_app.app_context():
            invitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_user=1)
            self.assertIsNotNone(invitation)

    def test_create_with_missing_expiration_date(self):
        """
        Test creating an invitation with missing expiration date will raise an IntegrityError.
        """
        with self._flask_app.app_context():
            with self.assertRaises(IntegrityError):
                invitation = TeraTestInvitation()
                invitation.id_test_type = 1
                invitation.id_user = 1
                TeraTestInvitation.insert(invitation)

    def test_create_with_automatic_key_generation(self):
        """
        Test creating an invitation with missing message.
        """
        with self._flask_app.app_context():
            invitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_user=1)
            self.assertIsNotNone(invitation)
            self.assertEqual(len(invitation.test_invitation_key), 16)

    def test_create_with_invalid_key(self):
        """
        Test creating an invitation with an invalid key will raise an IntegrityError.
        """
        with self._flask_app.app_context():
            with self.assertRaises(IntegrityError):
                invitation = TeraTestInvitation()
                invitation.id_test_type = 1
                invitation.id_user = 1
                invitation.test_invitation_key = "Invalid key"
                TeraTestInvitation.insert(invitation)

    def test_create_1000_invitations_should_have_different_keys(self):
        """
        Test creating 1000 invitations should have different keys.
        """
        with self._flask_app.app_context():
            keys = set()
            for _ in range(1000):
                invitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_user=1)
                self.assertNotIn(invitation.test_invitation_key, keys)
                keys.add(invitation.test_invitation_key)


    def test_update_test_type_should_raise_integrity_error(self):
        """
        Test updating the test type of an invitation will raise an IntegrityError.
        """
        with self._flask_app.app_context():
            invitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_user=1)
            with self.assertRaises(IntegrityError):
                invitation.id_test_type = 2
                TeraTestInvitation.update(invitation.id_test_invitation,
                                          TeraTestInvitation.clean_values(invitation.to_json()))

    def test_update_invitation_key_should_raise_integrity_error(self):
        """
        Test updating the key of an invitation will raise an IntegrityError.
        """
        with self._flask_app.app_context():
            invitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_user=1)
            with self.assertRaises(IntegrityError):
                invitation.test_invitation_key = "New key"
                TeraTestInvitation.update(invitation.id_test_invitation,
                                          TeraTestInvitation.clean_values(invitation.to_json()))

    @staticmethod
    def new_test_invitation(id_test_type: int,
                       id_session: int = None,
                       id_user: int = None,
                       id_participant: int = None,
                       id_device: int = None) -> TeraTestInvitation:
        """
        Insert a new test invitation in database.
        """

        invitation = TeraTestInvitation()

        invitation.id_test_type = id_test_type
        invitation.id_session = id_session
        invitation.id_user = id_user
        invitation.id_participant = id_participant
        invitation.id_device = id_device

        invitation.test_invitation_expiration_date = datetime.now(tz=timezone.utc) + timedelta(days=1)
        invitation.test_invitation_message = "Test invitation message"
        TeraTestInvitation.insert(invitation)
        return invitation
