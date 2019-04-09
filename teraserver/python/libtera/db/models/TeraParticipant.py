from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraKit import kits_participants_table
from libtera.db.models.TeraSession import sessions_participants_table
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
import uuid
import jwt
import time
import datetime


class TeraParticipant(db.Model, BaseModel):
    secret = 'TeraParticipant'
    __tablename__ = 't_participants'
    id_participant = db.Column(db.Integer, db.Sequence('id_participant_sequence'), primary_key=True, autoincrement=True)
    participant_uuid = db.Column(db.String(36), nullable=False, unique=True)
    participant_name = db.Column(db.String, nullable=False)
    participant_token = db.Column(db.String, nullable=False, unique=True)
    participant_lastonline = db.Column(db.TIMESTAMP, nullable=True)
    id_participant_group = db.Column(db.Integer, db.ForeignKey('t_participants_groups.id_participant_group',
                                                               ondelete='cascade'),
                                     nullable=False)

    participant_kits = db.relationship("TeraKit", secondary=kits_participants_table, back_populates="kit_participants",
                                       cascade="all,delete")

    participant_sessions = db.relationship("TeraSession", secondary=sessions_participants_table,
                                           back_populates="session_participants", cascade="all,delete")

    participant_participant_group = db.relationship('TeraParticipantGroup')

    def __str__(self):
        return '<TeraParticipant ' + str(self.participant_name) + ' >'

    def __repr__(self):
        return self.__str__()

    def create_token(self):
        # Creating token with user info
        payload = {
            'iat': int(time.time()),
            'participant_uuid': self.participant_uuid,
            'participant_name': self.participant_name
        }

        # TODO key should be secret ?
        self.participant_token = jwt.encode(payload, TeraParticipant.secret, 'HS256').decode('utf-8')

        return self.participant_token

    def update_last_online(self):
        self.participant_lastonline = datetime.datetime.now()
        db.session.commit()

    @staticmethod
    def get_participant_by_token(token):
        participant = TeraParticipant.query.filter_by(participant_token=token).first()

        if participant:
            # Validate token
            data = jwt.decode(token.encode('utf-8'), TeraParticipant.secret, 'HS256')

            if data['participant_uuid'] == participant.participant_uuid \
                    and data['participant_name'] == participant.participant_name:

                # Update last online
                participant.update_last_online()

                return participant
            else:
                return None

        return None

    @staticmethod
    def get_participant_by_name(name):
        return TeraParticipant.query.filter_by(participant_name=name).first()

    @staticmethod
    def create_defaults():
        participant1 = TeraParticipant()
        participant1.participant_name = 'Test Participant #1'
        participant1.participant_uuid = str(uuid.uuid4())
        participant1.participant_participant_group = \
            TeraParticipantGroup.get_participant_group_by_group_name('Default Participant Group')

        token1 = participant1.create_token()
        print('token1 ', token1)
        db.session.add(participant1)

        participant2 = TeraParticipant()
        participant2.participant_name = 'Test Participant #2'
        participant2.participant_uuid = str(uuid.uuid4())
        participant2.participant_participant_group = \
            TeraParticipantGroup.get_participant_group_by_group_name('Default Participant Group')

        token2 = participant2.create_token()
        print('token2 ', token2)
        db.session.add(participant2)

        db.session.commit()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraParticipant.id_participant))
        return count.first()[0]
