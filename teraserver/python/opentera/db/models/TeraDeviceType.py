from opentera.db.Base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship


class TeraDeviceType(BaseModel):

    __tablename__ = 't_devices_types'
    id_device_type = Column(Integer, Sequence('id_device_type_sequence'), primary_key=True, autoincrement=True)
    device_type_name = Column(String, nullable=False)
    device_type_key = Column(String, nullable=False, unique=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        device_type_json = super().to_json(ignore_fields=ignore_fields)

        return device_type_json

    def get_name(self) -> str:
        return self.device_type_name

    @staticmethod
    def create_defaults(test=False):
        # For now Defaults are hard coded
        VIDEOCONFERENCE = TeraDeviceType()
        VIDEOCONFERENCE.device_type_name = 'Vidéoconférence'
        VIDEOCONFERENCE.device_type_key = 'videoconference'
        TeraDeviceType.db().session.add(VIDEOCONFERENCE)

        CAPTEUR = TeraDeviceType()
        CAPTEUR.device_type_name = 'Capteur'
        CAPTEUR.device_type_key = 'capteur'
        TeraDeviceType.db().session.add(CAPTEUR)

        ROBOT = TeraDeviceType()
        ROBOT.device_type_name = 'Robot'
        ROBOT.device_type_key = 'robot'
        TeraDeviceType.db().session.add(ROBOT)

        BUREAU_ACTIF = TeraDeviceType()
        BUREAU_ACTIF.device_type_name = 'Bureau Actif'
        BUREAU_ACTIF.device_type_key = 'bureau_actif'
        TeraDeviceType.db().session.add(BUREAU_ACTIF)

    @staticmethod
    def get_devices_types():
        return TeraDeviceType.query.all()

    @staticmethod
    def get_device_type(dev_type: int):
        return TeraDeviceType.query.filter_by(id_device_type=dev_type).first()

    @staticmethod
    def get_device_type_by_id(dev_id: int):
        return TeraDeviceType.query.filter_by(id_device_type=dev_id).first()

    @staticmethod
    def get_device_type_by_name(dev_name: str):
        return TeraDeviceType.query.filter_by(device_type_name=dev_name).all()

    @staticmethod
    def get_device_type_by_key(dev_key: str):
        return TeraDeviceType.query.filter_by(device_type_key=dev_key).first()

    @staticmethod
    def commit():
        TeraDeviceType.db().session.commit()

