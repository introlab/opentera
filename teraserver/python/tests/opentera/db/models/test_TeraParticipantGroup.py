from tests.opentera.db.models.BaseModelsTest import BaseModelsTest

from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup


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
        pass
