from opentera.db.Base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship


class TeraSessionDevices(BaseModel):
    __tablename__ = 't_sessions_devices'
    id_session_device = Column(Integer, Sequence('id_session_device'), primary_key=True, autoincrement=True)
    id_session = Column(Integer, ForeignKey('t_sessions.id_session', ondelete='cascade'))
    id_device = Column(Integer, ForeignKey('t_devices.id_device'))

    session_device_session = relationship('TeraSession', viewonly=True)
    session_device_device = relationship('TeraDevice', viewonly=True)
