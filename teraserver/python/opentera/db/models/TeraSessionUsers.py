from opentera.db.Base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship


class TeraSessionUsers(BaseModel):
    __tablename__ = 't_sessions_users'
    id_session_user = Column(Integer, Sequence('id_session_user'), primary_key=True, autoincrement=True)
    id_session = Column(Integer, ForeignKey('t_sessions.id_session', ondelete='cascade'))
    id_user = Column(Integer, ForeignKey('t_users.id_user'))

    session_user_session = relationship('TeraSession', viewonly=True)
    session_user_user = relationship('TeraUser', viewonly=True)
