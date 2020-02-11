from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.models.TeraServerSettings import TeraServerSettings

import uuid
import jwt
import time
import datetime


class TeraParticipant(db.Model, BaseModel):
    __tablename__ = 't_participants'
    id_participant = db.Column(db.Integer, db.Sequence('id_participant_sequence'), primary_key=True, autoincrement=True)
    participant_uuid = db.Column(db.String(36), nullable=False, unique=True)
    participant_code = db.Column(db.String, nullable=False)
    participant_username = db.Column(db.String(50), nullable=True, unique=True)
    participant_email = db.Column(db.String, nullable=True, unique=True)
    participant_firstname = db.Column(db.String, nullable=True)
    participant_lastname = db.Column(db.String, nullable=True)
    participant_password = db.Column(db.String, nullable=True)
    participant_token = db.Column(db.String, nullable=False, unique=True)
    participant_lastonline = db.Column(db.TIMESTAMP, nullable=True)
    participant_active = db.Column(db.Boolean, nullable=False, default=True)
    participant_login_enabled = db.Column(db.Boolean, nullable=False, default=False)
    id_participant_group = db.Column(db.Integer, db.ForeignKey('t_participants_groups.id_participant_group',
                                                               ondelete='cascade'),
                                     nullable=False)
    participant_devices = db.relationship("TeraDeviceParticipant")

    participant_sessions = db.relationship("TeraSession", secondary="t_sessions_participants",
                                           back_populates="session_participants")

    participant_participant_group = db.relationship('TeraParticipantGroup')

    def __init__(self):
        pass

    def __str__(self):
        return '<TeraParticipant ' + str(self.participant_name) + ' >'

    def __repr__(self):
        return self.__str__()

    def create_token(self):
        # Creating token with user info
        payload = {
            'iat': int(time.time()),
            'participant_uuid': self.participant_uuid
        }

        # TODO key should be secret ?
        self.participant_token = jwt.encode(payload, TeraServerSettings.get_server_setting_value(
            TeraServerSettings.ServerParticipantTokenKey), algorithm='HS256').decode('utf-8')

        return self.participant_token

    def update_last_online(self):
        self.participant_lastonline = datetime.datetime.now()
        db.session.commit()

    def to_json(self, ignore_fields=[], minimal=False):

        ignore_fields.extend(['participant_participant_group', 'participant_devices',
                              'participant_token', 'participant_sessions', 'participant_password'])
        if minimal:
            ignore_fields.extend([])

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_participant_by_token(token):
        participant = TeraParticipant.query.filter_by(participant_token=token).first()

        if participant:
            # Validate token
            data = jwt.decode(token.encode('utf-8'), TeraServerSettings.get_server_setting_value(
                TeraServerSettings.ServerParticipantTokenKey), algorithms='HS256')

            if data['participant_uuid'] == participant.participant_uuid:

                # Update last online
                # TOCHECK: Should it be really here???
                participant.update_last_online()

                return participant
            else:
                return None

        return None

    @staticmethod
    def get_participant_by_uuid(p_uuid):
        participant = TeraParticipant.query.filter_by(participant_uuid=p_uuid).first()

        if participant:
            participant.update_last_online()
            return participant

        return None

    @staticmethod
    def get_participant_by_username(username):
        return TeraParticipant.query.filter_by(participant_username=username).first()

    @staticmethod
    def get_participant_by_code(code):
        return TeraParticipant.query.filter_by(participant_code=code).first()

    @staticmethod
    def get_participant_by_id(part_id: int):
        return TeraParticipant.query.filter_by(id_participant=part_id).first()

    @staticmethod
    def create_defaults():
        participant1 = TeraParticipant()
        participant1.participant_code = 'TestP1'
        participant1.participant_firstname = 'Participant #1 First Name'
        participant1.participant_lastname = 'Participant #1 Last Name'
        participant1.participant_active = True
        participant1.participant_uuid = str(uuid.uuid4())
        participant1.participant_participant_group = \
            TeraParticipantGroup.get_participant_group_by_group_name('Default Participant Group A')

        token1 = participant1.create_token()
        print('token1 ', token1)
        db.session.add(participant1)

        participant2 = TeraParticipant()
        participant2.participant_code = 'TestP2'
        participant2.participant_firstname = 'Participant #2 First Name'
        participant2.participant_lastname = 'Participant #2 Last Name'
        participant2.participant_active = True
        participant2.participant_uuid = str(uuid.uuid4())
        participant2.participant_participant_group = \
            TeraParticipantGroup.get_participant_group_by_group_name('Default Participant Group B')

        token2 = participant2.create_token()
        print('token2 ', token2)
        db.session.add(participant2)

        db.session.commit()

    @classmethod
    def insert(cls, participant):
        participant.participant_lastonline = None
        participant.participant_uuid = str(uuid.uuid4())
        participant.create_token()
        super().insert(participant)

    @classmethod
    def delete(cls, id_todel: int):
        super().delete(id_todel)

        # Check if we need to delete orphan sessions (sessions that have no more participants left
        from libtera.db.models.TeraSession import TeraSession
        TeraSession.delete_orphaned_sessions(False)

        db.session.commit()
