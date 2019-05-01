from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraProject import TeraProject


class TeraParticipantGroup(db.Model, BaseModel):
    __tablename__ = 't_participants_groups'
    id_participant_group = db.Column(db.Integer, db.Sequence('id_participantgroup_sequence'), primary_key=True,
                                     autoincrement=True)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)
    participant_group_name = db.Column(db.String, nullable=False, unique=False)

    participant_group_project = db.relationship('TeraProject')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['participant_group_project'])
        rval = super().to_json(ignore_fields=ignore_fields)

        rval['project_name'] = self.participant_group_project.project_name
        # rval['id_site'] = self.participant_group_project.id_site
        return rval

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
    def create_defaults():
        base_pgroup = TeraParticipantGroup()
        base_pgroup.participant_group_name = 'Default Participant Group A'
        base_pgroup.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        db.session.add(base_pgroup)

        base_pgroup2 = TeraParticipantGroup()
        base_pgroup2.participant_group_name = 'Default Participant Group B'
        base_pgroup2.id_project = TeraProject.get_project_by_projectname('Default Project #2').id_project
        db.session.add(base_pgroup2)
        db.session.commit()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraParticipantGroup.id_participant_group))
        return count.first()[0]
