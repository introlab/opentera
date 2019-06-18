from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraKit import kits_participants_table
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup

from flask_sqlalchemy import event

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

    participant_kits = db.relationship("TeraKit", secondary=kits_participants_table, back_populates="kit_participants")

    participant_sessions = db.relationship("TeraSession", secondary="t_sessions_participants",
                                           back_populates="session_participants")

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

    def to_json(self, ignore_fields=[], minimal=False):

        ignore_fields.extend(['participant_kits', 'participant_participant_group',
                              'participant_token', 'participant_sessions', 'secret'])
        if minimal:
            ignore_fields.extend([])

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_participant_by_token(token):
        participant = TeraParticipant.query.filter_by(participant_token=token).first()

        if participant:
            # Validate token
            data = jwt.decode(token.encode('utf-8'), TeraParticipant.secret, 'HS256')

            if data['participant_uuid'] == participant.participant_uuid \
                    and data['participant_name'] == participant.participant_name:

                # Update last online
                # TOCHECK: Should it be really here???
                participant.update_last_online()

                return participant
            else:
                return None

        return None

    @staticmethod
    def get_participant_by_uuid(uuid):
        participant = TeraParticipant.query.filter_by(participant_uuid=uuid).first()

        if participant:
            participant.update_last_online()
            return participant

        return None

    @staticmethod
    def get_participant_by_name(name):
        return TeraParticipant.query.filter_by(participant_name=name).first()

    @staticmethod
    def get_participant_by_id(part_id: int):
        return TeraParticipant.query.filter_by(id_participant=part_id).first()

    @staticmethod
    def create_defaults():
        participant1 = TeraParticipant()
        participant1.participant_name = 'Test Participant #1'
        participant1.participant_uuid = str(uuid.uuid4())
        participant1.participant_participant_group = \
            TeraParticipantGroup.get_participant_group_by_group_name('Default Participant Group A')

        token1 = participant1.create_token()
        print('token1 ', token1)
        db.session.add(participant1)

        participant2 = TeraParticipant()
        participant2.participant_name = 'Test Participant #2'
        participant2.participant_uuid = str(uuid.uuid4())
        participant2.participant_participant_group = \
            TeraParticipantGroup.get_participant_group_by_group_name('Default Participant Group B')

        token2 = participant2.create_token()
        print('token2 ', token2)
        db.session.add(participant2)

        db.session.commit()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraParticipant.id_participant))
        return count.first()[0]

    @staticmethod
    def update_participant(id_participant: int, values={}):
        TeraParticipant.query.filter_by(id_participant=id_participant).update(values)
        db.session.commit()

    @staticmethod
    def insert_participant(participant):
        participant.id_participant = None
        db.session.add(participant)
        db.session.commit()

    @staticmethod
    def delete_participant(id_participant: int):
        part = TeraParticipant.query.filter_by(id_participant=id_participant).first()
        db.session.delete(part)
        # Check if we need to delete orphan sessions (sessions that have no more participants left
        from libtera.db.models.TeraSession import TeraSession
        orphans = TeraSession.query.outerjoin(TeraSession.session_participants).filter(
            TeraSession.session_participants == None).all()

        if orphans:
            for orphan in orphans:
                db.session.delete(orphan)
        db.session.commit()

# @event.listens_for(TeraParticipant, 'after_delete')
# def after_delete_trigger(mapper, connection, target):
#     # Check if we need to delete orphan sessions (sessions that have no more participants left
#     from libtera.db.models.TeraSession import TeraSession
#     orphans = TeraSession.query.outerjoin(TeraSession.session_participants).filter(
#         TeraSession.session_participants == None).all()
#
#     if orphans:
#         for orphan in orphans:
#             db.session.delete(orphan)
#         db.session.commit()

