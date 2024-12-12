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

    def test_to_json(self):
        """
        Test to_json method
        """
        with self._flask_app.app_context():
            invitation1 : TeraTestInvitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_user=1)
            invitation2 : TeraTestInvitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_participant=1)
            invitation3 : TeraTestInvitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_device=1)
            invitation4 : TeraTestInvitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_session=1, id_user=1)

            for invitation in [invitation1, invitation2, invitation3, invitation4]:
                self._verify_to_json(invitation, minimal=True)
                self._verify_to_json(invitation, minimal=False)

    def test_from_json(self):
        """
        Test from_json method
        """
        with self._flask_app.app_context():
            invitation1 : TeraTestInvitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_user=1)
            invitation2 : TeraTestInvitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_participant=1)
            invitation3 : TeraTestInvitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_device=1)
            invitation4 : TeraTestInvitation = TeraTestInvitationTest.new_test_invitation(id_test_type=1, id_session=1, id_user=1)

            for invitation in [invitation1, invitation2, invitation3, invitation4]:
                invitation_json = invitation.to_json(minimal=True)
                new_invitation = TeraTestInvitation()
                new_invitation.from_json(invitation_json)
                self.assertEqual(invitation_json, new_invitation.to_json(minimal=True))

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

    def _verify_to_json(self, invitation : TeraTestInvitation, minimal: bool = False):

        invitation_json = invitation.to_json(minimal=minimal)
        self.assertTrue('id_test_invitation' in invitation_json)
        self.assertEqual(invitation_json['id_test_invitation'], invitation.id_test_invitation)
        self.assertTrue('id_test_type' in invitation_json)
        self.assertEqual(invitation_json['id_test_type'], invitation.id_test_type)
        self.assertTrue('id_user' in invitation_json)
        self.assertEqual(invitation_json['id_user'], invitation.id_user)
        self.assertTrue('id_participant' in invitation_json)
        self.assertEqual(invitation_json['id_participant'], invitation.id_participant)
        self.assertTrue('id_device' in invitation_json)
        self.assertEqual(invitation_json['id_device'], invitation.id_device)
        self.assertTrue('id_session' in invitation_json)
        self.assertEqual(invitation_json['id_session'], invitation.id_session)
        self.assertTrue('test_invitation_key' in invitation_json)
        self.assertEqual(invitation_json['test_invitation_key'], invitation.test_invitation_key)
        self.assertTrue('test_invitation_message' in invitation_json)
        self.assertEqual(invitation_json['test_invitation_message'], invitation.test_invitation_message)
        self.assertTrue('test_invitation_creation_date' in invitation_json)
        self.assertEqual(invitation_json['test_invitation_creation_date'], invitation.test_invitation_creation_date.isoformat())
        self.assertTrue('test_invitation_expiration_date' in invitation_json)
        self.assertEqual(invitation_json['test_invitation_expiration_date'], invitation.test_invitation_expiration_date.isoformat())
        self.assertTrue('test_invitation_max_count' in invitation_json)
        self.assertEqual(invitation_json['test_invitation_max_count'], invitation.test_invitation_max_count)
        self.assertTrue('test_invitation_count' in invitation_json)
        self.assertEqual(invitation_json['test_invitation_count'], invitation.test_invitation_count)

        if minimal:
            self.assertEqual(len(invitation_json), 12)
            self.assertFalse('test_invitation_test_type' in invitation_json)
            self.assertFalse('test_invitation_session' in invitation_json)
            self.assertFalse('test_invitation_user' in invitation_json)
            self.assertFalse('test_invitation_participant' in invitation_json)
            self.assertFalse('test_invitation_device' in invitation_json)
        else:
            count = 13
            self.assertTrue('test_invitation_test_type' in invitation_json)

            if invitation.id_session:
                count += 1
                self.assertTrue('test_invitation_session' in invitation_json)

            if invitation.id_user:
                count += 1
                self.assertTrue('test_invitation_user' in invitation_json)

            if invitation.id_participant:
                count += 1
                self.assertTrue('test_invitation_participant' in invitation_json)

            if invitation.id_device:
                count += 1
                self.assertTrue('test_invitation_device' in invitation_json)

            self.assertEqual(len(invitation_json), count)
