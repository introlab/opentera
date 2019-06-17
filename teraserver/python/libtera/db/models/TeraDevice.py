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
    id_site = db.Column(db.Integer, db.ForeignKey("t_sites.id_site", ondelete='cascade'), nullable=False)
    device_uuid = db.Column(db.String(36), nullable=False, unique=True)
    device_name = db.Column(db.String, nullable=False)
    device_type = db.Column(db.Integer, db.ForeignKey('t_devices_types.id_device_type', ondelete='cascade'),
                            nullable=False)
    device_token = db.Column(db.String, nullable=False, unique=True)
    device_enabled = db.Column(db.Boolean, nullable=False)
    device_onlineable = db.Column(db.Boolean, nullable=False)
    device_profile = db.Column(db.String, nullable=True)
    device_notes = db.Column(db.String, nullable=True)
    device_lastonline = db.Column(db.TIMESTAMP, nullable=True)

    device_kits = db.relationship("TeraKitDevice")
    device_site = db.relationship("TeraSite")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields += ['device_kits', 'device_site', 'device_token', 'secret']

        if minimal:
            ignore_fields += ['device_type', 'device_uuid', 'device_onlineable', 'device_profile', 'device_notes',
                              'device_lastonline']

        return super().to_json(ignore_fields=ignore_fields)

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
                    and data['device_name'] == device.device_name \
                    and data['device_type'] == device.device_type:

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
    def get_device_by_id(device_id):
        return TeraDevice.query.filter_by(id_device=device_id).first()

    @staticmethod
    def get_available_devices(ignore_disabled=True):
        if ignore_disabled:
            return TeraDevice.query.outerjoin(TeraDevice.device_kits).filter(TeraDevice.device_kits == None).all()
        else:
            return TeraDevice.query.filter_by(device_enabled=True).outerjoin(TeraDevice.device_kits).\
                filter(TeraDevice.device_kits == None).all()

    @staticmethod
    def get_unavailable_devices(ignore_disabled=True):
        if ignore_disabled:
            return TeraDevice.query.join(TeraDevice.device_kits).all()
        else:
            return TeraDevice.query.filter_by(device_enabled=True).join(TeraDevice.device_kits).all()

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraSite import TeraSite
        from libtera.db.models.TeraKitDevice import TeraKitDevice
        from libtera.db.models.TeraKit import TeraKit

        device = TeraDevice()
        device.device_name = 'Apple Watch #W05P1'
        # Forcing uuid for tests
        device.device_uuid = 'b707e0b2-e649-47e7-a938-2b949c423f73'  # str(uuid.uuid4())
        device.device_type = TeraDeviceType.DeviceTypeEnum.SENSOR.value
        device.create_token()
        device.device_enabled = True
        device.device_onlineable = True
        # device.device_project = TeraProject.get_project_by_projectname('Default Project #1')
        device.device_site = TeraSite.get_site_by_sitename('Default Site')

        kit = TeraKit.get_kit_by_name('Kit #1')
        kitDev = TeraKitDevice()
        kitDev.kit_device_kit = kit
        kitDev.kit_device_device = device
        kitDev.kit_device_optional = True
        device.device_kits.append(kitDev)
        db.session.add(device)

        device2 = TeraDevice()
        device2.device_name = 'Kit Télé #1'
        device2.device_uuid = str(uuid.uuid4())
        device2.device_type = TeraDeviceType.DeviceTypeEnum.VIDEOCONFERENCE.value
        device2.create_token()
        device2.device_enabled = True
        device2.device_onlineable = True
        # device.device_project = TeraProject.get_project_by_projectname('Default Project #1')
        device2.device_site = TeraSite.get_site_by_sitename('Default Site')
        db.session.add(device2)

        device3 = TeraDevice()
        device3.device_name = 'Robot A'
        device3.device_uuid = str(uuid.uuid4())
        device3.device_type = TeraDeviceType.DeviceTypeEnum.ROBOT.value
        device3.create_token()
        device3.device_enabled = True
        device3.device_onlineable = True
        # device.device_project = TeraProject.get_project_by_projectname('Default Project #1')
        device3.device_site = TeraSite.get_site_by_sitename('Default Site')
        db.session.add(device3)

        db.session.commit()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraDevice.id_device))
        return count.first()[0]

    @staticmethod
    def update_device(id_device, values={}):
        TeraDevice.query.filter_by(id_device=id_device).update(values)
        db.session.commit()

    @staticmethod
    def insert_device(device):
        device.id_device = None

        # Generate UUID
        device.device_uuid = str(uuid.uuid4())

        # Clear last online field
        device.device_lastonline = None

        # Create token
        device.create_token()

        db.session.add(device)
        db.session.commit()

    @staticmethod
    def delete_device(id_device):
        TeraDevice.query.filter_by(id_device=id_device).delete()
        db.session.commit()
