from libtera.db.Base import db, BaseModel
from enum import Enum, unique


class TeraDeviceType(db.Model, BaseModel):

    @unique
    class DeviceTypeEnum(Enum):
        VIDEOCONFERENCE = 1
        ROBOT = 2
        SENSOR = 3

        def describe(self):
            return self.name, self.value

    __tablename__ = 't_devices_types'
    id_device_type = db.Column(db.Integer, db.Sequence('id_device_sequence'), primary_key=True, autoincrement=True)
    device_type_name = db.Column(db.String, nullable=False)

    @staticmethod
    def create_defaults():
        for name, member in TeraDeviceType.DeviceTypeEnum.__members__.items():
            devType = TeraDeviceType()
            devType.device_type_name = name
            db.session.add(devType)

        db.session.commit()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraDeviceType.id_device_type))
        return count.first()[0]

    @staticmethod
    def get_devices_types():
        return TeraDeviceType.query.all()

