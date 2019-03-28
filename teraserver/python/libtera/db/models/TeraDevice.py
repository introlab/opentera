from libtera.db.Base import db, BaseModel
from enum import Enum


class TeraDeviceTypes(Enum):
    VIDEOCONFERENCE = 1
    ROBOT = 2
    SENSOR = 3


class TeraDevice(db.Model, BaseModel):
    __tablename__ = 't_devices'
    id_device = db.Column(db.Integer, db.Sequence('id_device_sequence'), primary_key=True, autoincrement=True)
    id_kit = db.Column(db.Integer, db.ForeignKey("t_kits.id_kit"), nullable=True)
    device_uuid = db.Column(db.String(36), nullable=False, unique=True)
    device_name = db.Column(db.String, nullable=False)
    device_type = db.Column(db.Integer, nullable=False)
    device_token = db.Column(db.String(36), nullable=False)
    device_enabled = db.Column(db.Boolean, nullable=False)
    device_onlineable = db.Column(db.Boolean, nullable=False)
    device_profile = db.Column(db.String, nullable=True)
    device_notes = db.Column(db.String, nullable=True)
    device_lastonline = db.Column(db.TIMESTAMP, nullable=True)

