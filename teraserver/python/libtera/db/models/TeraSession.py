from libtera.db.Base import db, BaseModel
from enum import Enum

sessions_participants_table = db.Table('t_sessions_participants', db.Column('id_session', db.Integer,
                                                                            db.ForeignKey('t_sessions.id_session')),
                                       db.Column('id_participant', db.Integer,
                                                 db.ForeignKey('t_participants.id_participant')))


class TeraSessionStatus(Enum):
    STATUS_NOTSTARTED = 0
    STATUS_INPROGRESS = 1
    STATUS_COMPLETED = 2
    STATUS_CANCELLED = 3
    STATUS_TERMINATED = 4


class TeraSession(db.Model, BaseModel):
    __tablename__ = 't_sessions'
    id_session = db.Column(db.Integer, db.Sequence('id_session_sequence'), primary_key=True, autoincrement=True)
    id_session_type = db.Column(db.Integer, db.ForeignKey('t_sessions_types.id_session_type'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user'), nullable=False)
    session_name = db.Column(db.String, nullable=False)
    session_datetime = db.Column(db.TIMESTAMP, nullable=False)
    session_status = db.Column(db.Integer, nullable=False)
    session_comments = db.Column(db.String, nullable=True)
    session_participants = db.relationship("TeraParticipant", secondary=sessions_participants_table,
                                           back_populates="participant_sessions", cascade="all,delete")

    session_user = db.relationship('TeraUser')
    session_session_type = db.relationship('TeraSessionType')

