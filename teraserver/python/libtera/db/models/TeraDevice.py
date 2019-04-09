from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraDeviceType import TeraDeviceType
import uuid
import jwt
import time
import datetime


class TeraDevice(db.Model, BaseModel):
    __tablename__ = 't_devices'
    secret = 'TeraDeviceSecret'
    id_device = db.Column(db.Integer, db.Sequence('id_device_sequence'), primary_key=True, autoincrement=True)
    id_kit = db.Column(db.Integer, db.ForeignKey("t_kits.id_kit"), nullable=True)
    device_uuid = db.Column(db.String(36), nullable=False, unique=True)
    device_name = db.Column(db.String, nullable=False)
    device_type = db.Column(db.Integer, db.ForeignKey('t_devices_types.id_device_type'), nullable=False)
    device_token = db.Column(db.String, nullable=False, unique=True)
    device_enabled = db.Column(db.Boolean, nullable=False)
    device_onlineable = db.Column(db.Boolean, nullable=False)
    device_profile = db.Column(db.String, nullable=True)
    device_notes = db.Column(db.String, nullable=True)
    device_lastonline = db.Column(db.TIMESTAMP, nullable=True)

    def create_token(self):
        # Creating token with user info
        payload = {
            'iat': int(time.time()),
            'device_uuid': self.device_uuid,
            'device_name': self.device_name,
            'device_type': self.device_type
        }

        # TODO key should be secret ?
        self.device_token = jwt.encode(payload, TeraDevice.secret, 'HS256').decode('utf-8')

        return self.device_token

    def update_last_online(self):
        self.device_lastonline = datetime.datetime.now()
        db.session.commit()

    @staticmethod
    def get_device_by_token(token):
        device = TeraDevice.query.filter_by(device_token=token).first()

        if device:
            # Validate token
            data = jwt.decode(token.encode('utf-8'), TeraDevice.secret, 'HS256')

            if data['device_uuid'] == device.device_uuid \
                    and data['device_name'] == device.device_name:

                # Update last online
                device.update_last_online()

                return device
            else:
                return None

        return None

    @staticmethod
    def get_device_by_name(name):
        return TeraDevice.query.filter_by(device_name=name).first()

    @staticmethod
    def create_defaults():
        device = TeraDevice()
        device.device_name = 'Apple Watch #W05P1'
        device.device_uuid = str(uuid.uuid4())
        device.device_type = TeraDeviceType.DeviceTypeEnum.SENSOR.value
        device.create_token()
        device.device_enabled = True
        device.device_onlineable = True
        db.session.add(device)
        db.session.commit()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraDevice.id_device))
        return count.first()[0]
