from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from opentera.db.SoftInsertMixin import SoftInsertMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship


class TeraSessionParticipants(BaseModel, SoftDeleteMixin, SoftInsertMixin):
    __tablename__ = 't_sessions_participants'
    id_session_participant = Column(Integer, Sequence('id_session_participant'), primary_key=True, autoincrement=True)
    id_session = Column(Integer, ForeignKey('t_sessions.id_session', ondelete='cascade'))
    id_participant = Column(Integer, ForeignKey('t_participants.id_participant'))

    session_participant_session = relationship('TeraSession', viewonly=True)
    session_participant_participant = relationship('TeraParticipant', viewonly=True)

    @staticmethod
    def get_session_count_for_participant(id_participant: int, with_deleted: bool = False) -> int:
        return TeraSessionParticipants.get_count(filters={'id_participant': id_participant}, with_deleted=with_deleted)

    @classmethod
    def update(cls, update_id: int, values: dict):
        return

