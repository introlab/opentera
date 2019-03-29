from libtera.db.Base import db, BaseModel


class TeraDeviceData(db.Model, BaseModel):
    __tablename__ = "t_devices_data"
    id_device_data = db.Column(db.Integer, db.Sequence("id_device_data_sequence"), primary_key=True, autoincrement=True)
    id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device"), nullable=False)
    id_session = db.Column(db.Integer, db.ForeignKey("t_sessions.id_session"), nullable=False)
    devicedata_name = db.Column(db.String, nullable=False)
    devicedata_original_filename = db.Column(db.String, nullable=False)
    devicedata_saved_date = db.Column(db.TIMESTAMP, nullable=False)

