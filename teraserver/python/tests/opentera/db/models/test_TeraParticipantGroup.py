from tests.opentera.db.models.BaseModelsTest import BaseModelsTest

from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraProject import TeraProject
from sqlalchemy.exc import IntegrityError


class TeraParticipantGroupTest(BaseModelsTest):

    def test_defaults(self):
        pass

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create a new participant group
            group = TeraParticipantGroup()
            group.participant_group_name = "Test participant group"
            group.id_project = 1
            TeraParticipantGroup.insert(group)
            self.assertIsNotNone(group.id_participant_group)
            id_participant_group = group.id_participant_group

            # Delete participant group
            TeraParticipantGroup.delete(id_participant_group)
            # Make sure participant group is deleted
            self.assertIsNone(TeraParticipantGroup.get_participant_group_by_id(id_participant_group))

            # Query, with soft delete flag
            group = TeraParticipantGroup.query.filter_by(id_participant_group=id_participant_group) \
                .execution_options(include_deleted=True).first()
            self.assertIsNotNone(group)
            self.assertIsNotNone(group.deleted_at)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create a new participant group
            group = TeraParticipantGroupTest.new_test_group()
            self.assertIsNotNone(group.id_participant_group)
            id_participant_group = group.id_participant_group

            # Create a new participant in that group
            from test_TeraParticipant import TeraParticipantTest
            participant = TeraParticipantTest.new_test_participant(id_project=1,
                                                                   id_participant_group=id_participant_group)
            self.assertIsNotNone(participant.id_participant)
            id_participant = participant.id_participant

            # Soft delete device to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraParticipant.delete(id_participant)
            TeraParticipantGroup.delete(id_participant_group)

            # Check that relationships are still there
            self.assertIsNone(TeraParticipant.get_participant_by_id(id_participant))
            self.assertIsNotNone(TeraParticipant.get_participant_by_id(id_participant, True))
            self.assertIsNone(TeraParticipantGroup.get_participant_group_by_id(id_participant_group))
            self.assertIsNotNone(TeraParticipantGroup.get_participant_group_by_id(id_participant_group, True))

            # Hard delete
            TeraParticipantGroup.delete(id_participant_group, hard_delete=True)

            # Make sure eveything is deleted
            self.assertIsNone(TeraParticipant.get_participant_by_id(id_participant, True))
            self.assertIsNone(TeraParticipantGroup.get_participant_group_by_id(id_participant_group, True))

    def test_undelete(self):
        with self._flask_app.app_context():
            # Create a new project
            from test_TeraProject import TeraProjectTest
            project = TeraProjectTest.new_test_project(id_site=1)
            id_project = project.id_project

            # Create a new participant group
            group = TeraParticipantGroupTest.new_test_group(id_project=id_project)
            self.assertIsNotNone(group.id_participant_group)
            id_participant_group = group.id_participant_group

            # Create a new participant in that group
            from test_TeraParticipant import TeraParticipantTest
            participant = TeraParticipantTest.new_test_participant(id_project=id_project,
                                                                   id_participant_group=id_participant_group)
            self.assertIsNotNone(participant.id_participant)
            id_participant = participant.id_participant

            # Soft delete device to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraParticipant.delete(id_participant)
            TeraParticipantGroup.delete(id_participant_group)

            # Undelete
            TeraParticipantGroup.undelete(id_participant_group)
            self.assertIsNotNone(TeraParticipantGroup.get_participant_group_by_id(id_participant_group))

            # ... delete again...
            TeraParticipantGroup.delete(id_participant_group)

            # ... but delete project before now
            TeraProject.delete(id_project)

            # Undelete will not work now...
            with self.assertRaises(IntegrityError) as cm:
                TeraParticipantGroup.undelete(id_participant_group)

            # But will if we restore the project beforehand!
            TeraProject.undelete(id_project)
            TeraParticipantGroup.undelete(id_participant_group)

            # Make sure eveything is Ok
            self.assertIsNone(TeraParticipant.get_participant_by_id(id_participant))
            self.assertIsNotNone(TeraParticipantGroup.get_participant_group_by_id(id_participant_group))

    @staticmethod
    def new_test_group(id_project: int = 1) -> TeraParticipantGroup:
        group = TeraParticipantGroup()
        group.participant_group_name = "Test Group"
        group.id_project = id_project
        TeraParticipantGroup.insert(group)
        return group
