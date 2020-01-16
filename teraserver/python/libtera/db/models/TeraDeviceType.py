from libtera.db.Base import db, BaseModel
from enum import Enum, unique


class TeraDeviceType(db.Model, BaseModel):

    @unique
    class DeviceTypeEnum(Enum):
        VIDEOCONFERENCE = 1
        ROBOT = 2
        SENSOR = 3
        BUREAU_ACTIF = 4

        def describe(self):
            return self.name, self.value

    __tablename__ = 't_devices_types'
    id_device_type = db.Column(db.Integer, db.Sequence('id_device_sequence'), primary_key=True, autoincrement=True)
    device_type_name = db.Column(db.String, nullable=False)

    device_type_session_types = db.relationship("TeraSessionTypeDeviceType")

    @staticmethod
    def create_defaults():
        for name, member in TeraDeviceType.DeviceTypeEnum.__members__.items():
            dev_type = TeraDeviceType()
            dev_type.id_device_type = member.value
            dev_type.device_type_name = name
            db.session.add(dev_type)

        db.session.commit()

    @staticmethod
    def get_devices_types():
        return TeraDeviceType.query.all()

    @staticmethod
    def get_device_type(dev_type: int):
        return TeraDeviceType.query.filter_by(id_device_type=dev_type).first()

    def get_name(self):
        name = 'Inconnu'
        if self.id_device_type == TeraDeviceType.DeviceTypeEnum.VIDEOCONFERENCE.value:
            name = 'Vidéoconférence'
        if self.id_device_type == TeraDeviceType.DeviceTypeEnum.SENSOR.value:
            name = 'Capteur'
        if self.id_device_type == TeraDeviceType.DeviceTypeEnum.ROBOT.value:
            name = 'Robot'
        if self.id_device_type == TeraDeviceType.DeviceTypeEnum.BUREAU_ACTIF.value:
            name = 'Bureau Actif'
        return name

