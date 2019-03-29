from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraProject import TeraProject


class TeraParticipantGroup(db.Model, BaseModel):
    __tablename__ = 't_participants_groups'
    id_participant_group = db.Column(db.Integer, db.Sequence('id_participantgroup_sequence'), primary_key=True,
                                     autoincrement=True)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project'), nullable=False)
    participantgroup_name = db.Column(db.String, nullable=False, unique=False)

    participantgroup_project = db.relationship('TeraProject')

    @staticmethod
    def create_defaults():
        base_pgroup = TeraParticipantGroup()
        base_pgroup.participantgroup_name = 'Default Participant Group'
        base_pgroup.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        db.session.add(base_pgroup)

        base_pgroup2 = TeraParticipantGroup()
        base_pgroup2.participantgroup_name = 'Default Participant Group'
        base_pgroup2.id_project = TeraProject.get_project_by_projectname('Default Project #2').id_project
        db.session.add(base_pgroup2)
        db.session.commit()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraParticipantGroup.id_participant_group))
        return count.first()[0]
