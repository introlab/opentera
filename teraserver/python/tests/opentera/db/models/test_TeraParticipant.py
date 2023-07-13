from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraService import TeraService

import uuid
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraParticipantTest(BaseModelsTest):

    def test_token(self):
        with self._flask_app.app_context():
            return
            participantGroup = TeraParticipantGroup()
            participantGroup.participant_group_name = 'participants'
            participantGroup.id_project = 1

            participant = TeraParticipant()
            participant.participant_name = 'Test Participant'
            participant.participant_uuid = str(uuid.uuid4())
            participant.participant_participant_group = participantGroup

            token = participant.create_token()

            self.assertNotEqual(token, "")
            self.db.session.add(participantGroup)
            self.db.session.add(participant)

            self.db.session.commit()

            # Load participant from invalid token
            loadedParticipant = TeraParticipant.get_participant_by_token('rien')
            self.assertEqual(loadedParticipant, None)

            # Load participant from valid token
            loadedParticipant = TeraParticipant.get_participant_by_token(token)
            self.assertEqual(loadedParticipant.participant_uuid, participant.participant_uuid)

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create a new participant
            participant = TeraParticipant()
            participant.participant_name = "Test participant"
            participant.id_project = 1
            TeraParticipant.insert(participant)
            self.assertIsNotNone(participant.id_participant)
            id_participant = participant.id_participant

            # Delete participant
            TeraParticipant.delete(id_participant)
            # Make sure participant is deleted
            self.assertIsNone(TeraParticipant.get_participant_by_id(id_participant))

            # Query, with soft delete flag
            participant = TeraParticipant.query.filter_by(id_participant=id_participant)\
                .execution_options(include_deleted=True).first()
            self.assertIsNotNone(participant)
            self.assertIsNotNone(participant.deleted_at)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create a new participant
            participant = TeraParticipant()
            participant.participant_name = "Test participant"
            participant.id_project = 1
            TeraParticipant.insert(participant)
            self.assertIsNotNone(participant.id_participant)
            id_participant = participant.id_participant

            # Assign participant to sessions
            part_session = TeraSession()
            part_session.id_creator_participant = id_participant
            part_session.id_session_type = 1
            part_session.session_name = 'Creator participant session'
            TeraSession.insert(part_session)
            id_session = part_session.id_session

            part_session = TeraSession()
            part_session.id_creator_service = 1
            part_session.id_session_type = 1
            part_session.session_name = "Participant invitee session"
            part_session.session_participants = [participant]
            TeraSession.insert(part_session)
            id_session_invitee = part_session.id_session

            # Attach asset
            asset = TeraAsset()
            asset.asset_name = "Participant asset test"
            asset.id_participant = id_participant
            asset.id_session = id_session
            asset.asset_service_uuid = TeraService.get_openteraserver_service().service_uuid
            asset.asset_type = 'Test'
            TeraAsset.insert(asset)
            id_asset = asset.id_asset

            # ... and test
            test = TeraTest()
            test.id_participant = id_participant
            test.id_session = id_session
            test.id_test_type = 1
            test.test_name = "Device test test!"
            TeraTest.insert(test)
            id_test = test.id_test

            # Soft delete device to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraSession.delete(id_session)
            TeraSession.delete(id_session_invitee)
            TeraParticipant.delete(id_participant)

            # Check that device and relationships are still there
            self.assertIsNone(TeraParticipant.get_participant_by_id(id_participant))
            self.assertIsNotNone(TeraParticipant.get_participant_by_id(id_participant, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session))
            self.assertIsNotNone(TeraSession.get_session_by_id(id_session, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session_invitee))
            self.assertIsNotNone(TeraSession.get_session_by_id(id_session_invitee, True))
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset))
            self.assertIsNotNone(TeraAsset.get_asset_by_id(id_asset, True))
            self.assertIsNone(TeraTest.get_test_by_id(id_test))
            self.assertIsNotNone(TeraTest.get_test_by_id(id_test, True))

            # Hard delete participant
            TeraParticipant.delete(participant.id_participant, hard_delete=True)

            # Make sure device and associations are deleted
            self.assertIsNone(TeraParticipant.get_participant_by_id(id_participant, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session, True))
            self.assertIsNone(TeraSession.get_session_by_id(id_session_invitee, True))
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset, True))
            self.assertIsNone(TeraTest.get_test_by_id(id_test, True))

