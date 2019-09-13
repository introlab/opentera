from libtera.db.Base import db, BaseModel

from enum import Enum, unique


class TeraSessionEvent(db.Model, BaseModel):
    @unique
    class SessionEventTypes(Enum):
        INFO = 1
        CONNECTED = 2
        DISCONNECTED = 3
        ERROR = 4
        WARNING = 5

    __tablename__ = 't_sessions_events'
    id_session_event = db.Column(db.Integer, db.Sequence('id_session_events_sequence'), primary_key=True,
                                 autoincrement=True)
    id_session = db.Column(db.Integer, db.ForeignKey('t_sessions.id_session', ondelete='cascade'), nullable=False)
    id_session_event_type = db.Column(db.Integer, nullable=False)
    session_event_datetime = db.Column(db.TIMESTAMP, nullable=False)
    session_event_text = db.Column(db.String, nullable=True)

    session_event_session = db.relationship('TeraSession')

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['session_event_session'])
        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def get_session_event_by_id(event_id: int):
        return TeraSessionEvent.query.filter_by(id_session_event=event_id).first()

    @staticmethod
    def get_events_for_session(id_session: int):
        from .TeraSession import TeraSession
        return db.session.query(TeraSessionEvent).join(TeraSessionEvent.session_event_session)\
            .filter(TeraSession.id_session == id_session)