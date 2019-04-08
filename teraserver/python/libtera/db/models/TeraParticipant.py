from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraKit import kits_participants_table
from libtera.db.models.TeraSession import sessions_participants_table
import jwt
import time


class TeraParticipant(db.Model, BaseModel):
    secret = 'TeraParticipant'
    __tablename__ = 't_participants'
    id_participant = db.Column(db.Integer, db.Sequence('id_participant_sequence'), primary_key=True, autoincrement=True)
    participant_uuid = db.Column(db.String(36), nullable=False, unique=True)
    participant_name = db.Column(db.String, nullable=False)
    participant_token = db.Column(db.String, nullable=False)
    participant_lastonline = db.Column(db.TIMESTAMP, nullable=True)
    id_participant_group = db.Column(db.Integer, db.ForeignKey('t_participants_groups.id_participant_group'),
                                     nullable=False)

    participant_kits = db.relationship("TeraKit", secondary=kits_participants_table, back_populates="kit_participants",
                                       cascade="all,delete")

    participant_sessions = db.relationship("TeraSession", secondary=sessions_participants_table,
                                           back_populates="session_participants", cascade="all,delete")

    participant_participant_group = db.relationship('TeraParticipantGroup')

    def create_token(self):
        # Creating token with user info
        payload = {
            'iat': int(time.time()),
            'participant_uuid': self.participant_uuid,
            'participant_name': self.participant_name
        }

        # TODO key should be secret ?
        self.participant_token = jwt.encode(payload, TeraParticipant.secret, 'HS256')

        return self.participant_token

    @staticmethod
    def get_participant_by_token(token):
        participant = TeraParticipant.query.filter_by(participant_token=token).first()

        if participant:
            # Validate token
            data = jwt.decode(token, TeraParticipant.secret, 'HS256')

            if data['participant_uuid'] == participant.participant_uuid \
                    and data['participant_name'] == participant.participant_name:
                return participant
            else:
                return None

        return None


    # @staticmethod
    # def create_defaults():
    #     base_pgroup = TeraParticipantGroup()
    #     base_pgroup.participantgroup_name = 'Default Group'
    #     base_pgroup.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
    #     db.session.add(base_pgroup)
    #
    #     base_pgroup2 = TeraParticipantGroup()
    #     base_pgroup2.participantgroup_name = 'Default Group'
    #     base_pgroup2.id_project = TeraProject.get_project_by_projectname('Default Project #2').id_project
    #     db.session.add(base_pgroup2)
    #     db.session.commit()
    #
    # @staticmethod
    # def get_count():
    #     count = db.session.query(db.func.count(TeraParticipantGroup.id_participant_group))
    #     return count.first()[0]
