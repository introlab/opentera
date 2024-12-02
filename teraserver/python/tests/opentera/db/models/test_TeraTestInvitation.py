from datetime import datetime, timezone, timedelta

from sqlalchemy.exc import IntegrityError

from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraTestInvitation import TeraTestInvitation
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraDevice import TeraDevice



class TeraTestInvitationTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    def test_db_events_not_none(self):
        with self._flask_app.app_context():
            invitation : TeraTestInvitation = TeraTestInvitationTest.new_invitation(id_test_type=1, id_user=1)
            self.assertIsNotNone(invitation.to_json_create_event())
            self.assertIsNotNone(invitation.to_json_update_event())
            self.assertIsNotNone(invitation.to_json_delete_event())

    @staticmethod
    def new_invitation(id_test_type: int,
                       id_session: int = None,
                       id_user: int = None,
                       id_participant: int = None,
                       id_device: int = None) -> TeraTestInvitation:

        invitation = TeraTestInvitation()

        invitation.id_test_type = id_test_type
        invitation.id_session = id_session
        invitation.id_user = id_user
        invitation.id_participant = id_participant
        invitation.id_device = id_device

        # Make sure only one of the 3 is set
        ids = [id_user, id_participant, id_device]
        if sum(x is not None for x in ids) != 1:
            raise ValueError("Only one of id_user, id_participant, id_device must be set")

        invitation.test_invitation_expiration_date = datetime.now(tz=timezone.utc) + timedelta(days=1)
        invitation.test_invitation_message = "Test invitation message"
        return invitation
