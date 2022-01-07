from opentera.db.Base import db, BaseModel


class TeraSessionUsers(db.Model, BaseModel):
    __tablename__ = 't_sessions_users'
    id_session_user = db.Column(db.Integer, db.Sequence('id_session_user'), primary_key=True, autoincrement=True)
    id_session = db.Column(db.Integer, db.ForeignKey('t_sessions.id_session', ondelete='cascade'))
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user'))

    session_user_session = db.relationship('TeraSession', viewonly=True)
    session_user_user = db.relationship('TeraUser', viewonly=True)
