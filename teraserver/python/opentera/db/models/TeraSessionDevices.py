from opentera.db.Base import db, BaseModel


class TeraSessionDevices(db.Model, BaseModel):
    __tablename__ = 't_sessions_devices'
    id_session_device = db.Column(db.Integer, db.Sequence('id_session_device'), primary_key=True, autoincrement=True)
    id_session = db.Column(db.Integer, db.ForeignKey('t_sessions.id_session', ondelete='cascade'))
    id_device = db.Column(db.Integer, db.ForeignKey('t_devices.id_device'))

    session_device_session = db.relationship('TeraSession', viewonly=True)
    session_device_device = db.relationship('TeraDevice', viewonly=True)
