from libtera.db.Base import db, BaseModel


class TeraDevice(db.Model, BaseModel):
    __tablename__ = 't_devices'
    id_device = db.Column(db.Integer, db.Sequence('id_device_sequence'),
                          primary_key=True, autoincrement=True)
