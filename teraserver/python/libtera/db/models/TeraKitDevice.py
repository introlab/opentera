from libtera.db.Base import db, BaseModel


class TeraKitDevice(db.Model, BaseModel):
    __tablename__ = 't_kits_devices'
    id_kit_device = db.Column(db.Integer, db.Sequence('id_kit_device_sequence'), primary_key=True, autoincrement=True)
    id_kit = db.Column(db.Integer, db.ForeignKey("t_kits.id_kit", ondelete='cascade'), nullable=False)
    id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device", ondelete='cascade'), nullable=False)
    kit_device_optional = db.Column(db.Boolean, nullable=False)

    kit_device_kit = db.relationship("TeraKit")
    kit_device_device = db.relationship("TeraDevice")
