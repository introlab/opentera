from opentera.db.Base import db, BaseModel


class TeraSessionParticipants(db.Model, BaseModel):
    __tablename__ = 't_sessions_participants'
    id_session_participant = db.Column(db.Integer, db.Sequence('id_session_participant'), primary_key=True,
                                       autoincrement=True)
    id_session = db.Column(db.Integer, db.ForeignKey('t_sessions.id_session'))
    id_participant = db.Column(db.Integer, db.ForeignKey('t_participants.id_participant'))

    session_participant_session = db.relationship('TeraSession')
    session_participant_participant = db.relationship('TeraParticipant')
