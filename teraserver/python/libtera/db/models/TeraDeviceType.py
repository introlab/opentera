from libtera.db.Base import db, BaseModel


class TeraDeviceType(db.Model, BaseModel):

    __tablename__ = 't_devices_types'
    id_device_type = db.Column(db.Integer, db.Sequence('id_device_type_sequence'), primary_key=True, autoincrement=True)
    device_type_name = db.Column(db.String, nullable=False)
    device_type_key = db.Column(db.String, nullable=False, unique=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields += ['DeviceTypeEnum']

        device_type_json = super().to_json(ignore_fields=ignore_fields)

        return device_type_json

    @staticmethod
    def create_defaults():
        # For now Defaults are hard coded

        VIDEOCONFERENCE = TeraDeviceType()
        VIDEOCONFERENCE.device_type_name = 'VIDEOCONFERENCE'
        VIDEOCONFERENCE.device_type_key = 'videoconference'
        db.session.add(VIDEOCONFERENCE)

        CAPTEUR = TeraDeviceType()
        CAPTEUR.device_type_name = 'CAPTEUR'
        CAPTEUR.device_type_key = 'capteur'
        db.session.add(CAPTEUR)

        ROBOT = TeraDeviceType()
        ROBOT.device_type_name = 'ROBOT'
        ROBOT.device_type_key = 'robot'
        db.session.add(ROBOT)

        BUREAU_ACTIF = TeraDeviceType()
        BUREAU_ACTIF.device_type_name = 'BUREAU_ACTIF'
        BUREAU_ACTIF.device_type_key = 'bureau_actif'
        db.session.add(BUREAU_ACTIF)

    @staticmethod
    def get_devices_types():
        return TeraDeviceType.query.all()

    @staticmethod
    def get_device_type(dev_type: int):
        return TeraDeviceType.query.filter_by(id_device_type=dev_type).first()

    @staticmethod
    def get_device_type_by_id(dev_type: int):
        return TeraDeviceType.query.filter_by(id_device_type=dev_type).first()

    @staticmethod
    def get_device_type_by_name(dev_type: str):
        return TeraDeviceType.query.filter_by(device_type_name=dev_type).all()

    @staticmethod
    def get_device_type_by_key(dev_type: str):
        return TeraDeviceType.query.filter_by(device_type_key=dev_type).first()

    @staticmethod
    def get_device_type_by_type(dev_type: str):
        return TeraDeviceType.query.filter_by(device_type_key=dev_type).first()

    @staticmethod
    def commit():
        db.session.commit()

