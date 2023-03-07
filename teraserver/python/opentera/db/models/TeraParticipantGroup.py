from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from opentera.db.models.TeraProject import TeraProject


class TeraParticipantGroup(BaseModel, SoftDeleteMixin):
    __tablename__ = 't_participants_groups'
    id_participant_group = Column(Integer, Sequence('id_participantgroup_sequence'), primary_key=True,
                                  autoincrement=True)
    id_project = Column(Integer, ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)
    participant_group_name = Column(String, nullable=False, unique=False)

    participant_group_project = relationship('TeraProject', back_populates='project_participants_groups')
    participant_group_participants = relationship("TeraParticipant", back_populates='participant_participant_group',
                                                  passive_deletes=True, cascade='delete')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['participant_group_project', 'participant_group_participants'])
        rval = super().to_json(ignore_fields=ignore_fields)

        if not minimal:
            rval['project_name'] = self.participant_group_project.project_name
        # rval['id_site'] = self.participant_group_project.id_site
        return rval

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_participant_group': self.id_participant_group}

    @staticmethod
    def get_participant_group_by_group_name(name: str, with_deleted: bool = False):
        return TeraParticipantGroup.query.execution_options(include_deleted=with_deleted)\
            .filter_by(participant_group_name=name).first()

    @staticmethod
    def get_participant_group_by_id(group_id: int, with_deleted: bool = False):
        return TeraParticipantGroup.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_participant_group=group_id).first()

    @staticmethod
    def get_participant_group_for_project(project_id: int, with_deleted: bool = False):
        return TeraParticipantGroup.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_project=project_id).all()

    @staticmethod
    def create_defaults(test=False):
        if test:
            base_pgroup = TeraParticipantGroup()
            base_pgroup.participant_group_name = 'Default Participant Group A'
            base_pgroup.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
            TeraParticipantGroup.db().session.add(base_pgroup)

            base_pgroup2 = TeraParticipantGroup()
            base_pgroup2.participant_group_name = 'Default Participant Group B'
            base_pgroup2.id_project = TeraProject.get_project_by_projectname('Default Project #2').id_project
            TeraParticipantGroup.db().session.add(base_pgroup2)
            TeraParticipantGroup.db().session.commit()

    @classmethod
    def update(cls, update_id: int, values: dict):
        # If group project changed, also changed project from all participants in that group
        if 'id_project' in values:
            updated_group:TeraParticipantGroup = TeraParticipantGroup.get_participant_group_by_id(update_id)
            if updated_group:
                for participant in updated_group.participant_group_participants:
                    participant.id_project = values['id_project']
        super().update(update_id=update_id, values=values)

    def delete_check_integrity(self) -> IntegrityError | None:
        for participant in self.participant_group_participants:
            cannot_be_deleted_exception = participant.delete_check_integrity()
            if cannot_be_deleted_exception:
                return IntegrityError('Participant group still has participant(s)', self.id_participant_group,
                                      't_participants')
        return None
