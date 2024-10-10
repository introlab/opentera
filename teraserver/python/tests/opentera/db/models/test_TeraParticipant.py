from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraServiceConfig import TeraServiceConfig
from sqlalchemy.exc import IntegrityError

import uuid
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraParticipantTest(BaseModelsTest):

    def test_token(self):
        with self._flask_app.app_context():
            return
            # participantGroup = TeraParticipantGroup()
            # participantGroup.participant_group_name = 'participants'
            # participantGroup.id_project = 1
            #
            # participant = TeraParticipant()
            # participant.participant_name = 'Test Participant'
            # participant.participant_uuid = str(uuid.uuid4())
            # participant.participant_participant_group = participantGroup
            #
            # token = participant.create_token()
            #
            # self.assertNotEqual(token, "")
            # self.db.session.add(participantGroup)
            # self.db.session.add(participant)
            #
            # self.db.session.commit()
            #
            # # Load participant from invalid token
            # loadedParticipant = TeraParticipant.get_participant_by_token('rien')
            # self.assertEqual(loadedParticipant, None)
            #
            # # Load participant from valid token
            # loadedParticipant = TeraParticipant.get_participant_by_token(token)
            # self.assertEqual(loadedParticipant.participant_uuid, participant.participant_uuid)

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create a new participant
            participant = TeraParticipantTest.new_test_participant(id_project=1)
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
            participant = TeraParticipantTest.new_test_participant(id_project=1)
            self.assertIsNotNone(participant.id_participant)
            id_participant = participant.id_participant

            # Assign participant to sessions
            from tests.opentera.db.models.test_TeraSession import TeraSessionTest
            part_session = TeraSessionTest.new_test_session(id_creator_participant=id_participant)
            id_session = part_session.id_session

            part_session = TeraSessionTest.new_test_session(id_creator_service=1, participants=[participant])
            id_session_invitee = part_session.id_session

            # Attach asset
            from tests.opentera.db.models.test_TeraAsset import TeraAssetTest
            asset = TeraAssetTest.new_test_asset(id_session=id_session,
                                                 service_uuid=TeraService.get_openteraserver_service().service_uuid,
                                                 id_participant=id_participant)
            id_asset = asset.id_asset

            # ... and test
            from tests.opentera.db.models.test_TeraTest import TeraTestTest
            test = TeraTestTest.new_test_test(id_session=id_session, id_participant=id_participant)
            id_test = test.id_test

            # Soft delete device to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraSession.delete(id_session)
            TeraSession.delete(id_session_invitee)
            TeraParticipant.delete(id_participant)

            # Check that relationships are still there
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

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create a new project
            from tests.opentera.db.models.test_TeraProject import TeraProjectTest
            project = TeraProjectTest.new_test_project()
            id_project = project.id_project

            # Create a new participant
            participant = TeraParticipantTest.new_test_participant(id_project=id_project)
            self.assertIsNotNone(participant.id_participant)
            id_participant = participant.id_participant

            # Assign participant to sessions
            from tests.opentera.db.models.test_TeraSession import TeraSessionTest
            part_session = TeraSessionTest.new_test_session(id_creator_participant=id_participant)
            id_session = part_session.id_session

            part_session = TeraSessionTest.new_test_session(id_creator_service=1, participants=[participant])
            id_session_invitee = part_session.id_session

            # Attach asset
            from tests.opentera.db.models.test_TeraAsset import TeraAssetTest
            asset = TeraAssetTest.new_test_asset(id_session=id_session,
                                                 service_uuid=TeraService.get_openteraserver_service().service_uuid,
                                                 id_participant=id_participant)
            id_asset = asset.id_asset

            # ... and test
            from tests.opentera.db.models.test_TeraTest import TeraTestTest
            test = TeraTestTest.new_test_test(id_session=id_session, id_participant=id_participant)
            id_test = test.id_test

            # ... and service config
            from tests.opentera.db.models.test_TeraServiceConfig import TeraServiceConfigTest
            device_service_config = TeraServiceConfigTest.new_test_service_config(id_participant=id_participant,
                                                                                  id_service=2)
            id_service_config = device_service_config.id_service_config

            # Soft delete device to prevent relationship integrity errors as it's not what we want to test here
            TeraSession.delete(id_session)
            TeraSession.delete(id_session_invitee)
            TeraParticipant.delete(id_participant)

            # Undelete participant
            TeraParticipant.undelete(id_participant)

            # ... then delete it again...
            TeraParticipant.delete(id_participant)

            # ... and its project...
            TeraProject.delete(id_project)

            # Then undelete participant with an error
            with self.assertRaises(IntegrityError) as cm:
                TeraParticipant.undelete(id_participant)

            # Then undelete project...
            TeraProject.undelete(id_project)

            # And then undelete again!
            TeraParticipant.undelete(id_participant)

            # Create and associate participant group
            from tests.opentera.db.models.test_TeraParticipantGroup import TeraParticipantGroupTest
            group = TeraParticipantGroupTest.new_test_group(id_project)
            id_group = group.id_participant_group

            TeraParticipant.update(id_participant, {'id_participant_group': id_group})

            # Delete again...
            TeraParticipant.delete(id_participant)

            # ... and delete group
            TeraParticipantGroup.delete(id_group)

            # Then undelete participant with an error
            with self.assertRaises(IntegrityError) as cm:
                TeraParticipant.undelete(id_participant)

            # Restore group
            TeraParticipantGroup.undelete(id_group)

            # ... and participant
            TeraParticipant.undelete(id_participant)

            # Make sure associations are still deleted
            self.assertIsNotNone(TeraParticipant.get_participant_by_id(id_participant))
            self.assertIsNotNone(TeraParticipantGroup.get_participant_group_by_id(id_group))
            self.assertIsNone(TeraSession.get_session_by_id(id_session))
            self.assertIsNone(TeraSession.get_session_by_id(id_session_invitee))
            self.assertIsNone(TeraAsset.get_asset_by_id(id_asset))
            self.assertIsNone(TeraTest.get_test_by_id(id_test))
            self.assertIsNotNone(TeraServiceConfig.get_service_config_by_id(id_service_config))

    @staticmethod
    def new_test_participant(id_project: int, id_participant_group: int | None = None, enabled: bool = False) -> TeraParticipant:
        participant = TeraParticipant()
        participant.participant_name = "Test participant"
        participant.id_project = id_project
        if id_participant_group:
            participant.id_participant_group = id_participant_group
        participant.participant_enabled = enabled
        TeraParticipant.insert(participant)

        return participant
