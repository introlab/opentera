from libtera.db.Base import db, BaseModel

# class TeraDeviceTypes(Enum):
#     VIDEOCONFERENCE = 1
#     ROBOT = 2
#     SENSOR = 3


class TeraDeviceType(db.Model, BaseModel):
    __tablename__ = 't_devices_types'
    id_device_type = db.Column(db.Integer, db.Sequence('id_device_sequence'), primary_key=True, autoincrement=True)
    device_type_name = db.Column(db.String, nullable=False)
