from opentera.db.Base import db, BaseModel

from enum import Enum, unique
from datetime import datetime, timedelta
import random


class TeraSessionEvent(db.Model, BaseModel):
    @unique
    class SessionEventTypes(Enum):
        GENERAL_ERROR = 0
        GENERAL_INFO = 1
        GENERAL_WARNING = 2
        SESSION_START = 3
        SESSION_STOP = 4
        DEVICE_ON_CHARGE = 5
        DEVICE_OFF_CHARGE = 6
        DEVICE_LOW_BATT = 7
        DEVICE_STORAGE_LOW = 8
        DEVICE_STORAGE_FULL = 9
        DEVICE_EVENT = 10
        USER_EVENT = 11
        SESSION_JOIN = 12
        SESSION_LEAVE = 13
        SESSION_JOIN_REFUSED = 14

    __tablename__ = 't_sessions_events'
    id_session_event = db.Column(db.Integer, db.Sequence('id_session_events_sequence'), primary_key=True,
                                 autoincrement=True)
    id_session = db.Column(db.Integer, db.ForeignKey('t_sessions.id_session', ondelete='cascade'), nullable=False)
    id_session_event_type = db.Column(db.Integer, nullable=False)
    session_event_datetime = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    session_event_text = db.Column(db.String, nullable=True)
    session_event_context = db.Column(db.String, nullable=True)

    session_event_session = db.relationship('TeraSession')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['session_event_session', 'SessionEventTypes'])
        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraSession import TeraSession

            base_session = TeraSession.get_session_by_name('Séance #1')
            for i in range(12):
                event = TeraSessionEvent()
                event.session_event_session = base_session
                event.id_session_event_type = i
                event.session_event_datetime = datetime.now() - timedelta(hours=random.randint(0, 10)) - timedelta(
                    minutes=random.randint(0, 45))
                event.session_event_context = 'Défaut'
                event.session_event_text = str(TeraSessionEvent.SessionEventTypes(i))
                db.session.add(event)
            db.session.commit()

    @staticmethod
    def get_session_event_by_id(event_id: int):
        return TeraSessionEvent.query.filter_by(id_session_event=event_id).first()

    @staticmethod
    def get_events_for_session(id_session: int):
        from .TeraSession import TeraSession
        return db.session.query(TeraSessionEvent).join(TeraSessionEvent.session_event_session)\
            .filter(TeraSession.id_session == id_session)
