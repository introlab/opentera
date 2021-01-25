from opentera.db.Base import db, BaseModel
from opentera.db.models.TeraProject import TeraProject


class TeraParticipantGroup(db.Model, BaseModel):
    __tablename__ = 't_participants_groups'
    id_participant_group = db.Column(db.Integer, db.Sequence('id_participantgroup_sequence'), primary_key=True,
                                     autoincrement=True)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)
    participant_group_name = db.Column(db.String, nullable=False, unique=False)

    participant_group_project = db.relationship('TeraProject')
    participant_group_participants = db.relationship("TeraParticipant", passive_deletes=True)

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
    def get_participant_group_by_group_name(name: str):
        return TeraParticipantGroup.query.filter_by(participant_group_name=name).first()

    @staticmethod
    def get_participant_group_by_id(group_id: int):
        return TeraParticipantGroup.query.filter_by(id_participant_group=group_id).first()

    @staticmethod
    def get_participant_group_for_project(project_id: int):
        return TeraParticipantGroup.query.filter_by(id_project=project_id).all()

    @staticmethod
    def create_defaults(test=False):
        if test:
            base_pgroup = TeraParticipantGroup()
            base_pgroup.participant_group_name = 'Default Participant Group A'
            base_pgroup.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
            db.session.add(base_pgroup)

            base_pgroup2 = TeraParticipantGroup()
            base_pgroup2.participant_group_name = 'Default Participant Group B'
            base_pgroup2.id_project = TeraProject.get_project_by_projectname('Default Project #2').id_project
            db.session.add(base_pgroup2)
            db.session.commit()

    @classmethod
    def delete(cls, id_todel):
        super().delete(id_todel)

        # from opentera.db.models.TeraSession import TeraSession
        # TeraSession.delete_orphaned_sessions()
