from opentera.db.Base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship


class TeraSessionParticipants(BaseModel):
    __tablename__ = 't_sessions_participants'
    id_session_participant = Column(Integer, Sequence('id_session_participant'), primary_key=True,
                                       autoincrement=True)
    id_session = Column(Integer, ForeignKey('t_sessions.id_session'))
    id_participant = Column(Integer, ForeignKey('t_participants.id_participant'))

    session_participant_session = relationship('TeraSession', viewonly=True)
    session_participant_participant = relationship('TeraParticipant', viewonly=True)

    @staticmethod
    def get_session_count_for_participant(id_participant: int) -> int:
        return TeraSessionParticipants.count_with_filters({'id_participant': id_participant})
