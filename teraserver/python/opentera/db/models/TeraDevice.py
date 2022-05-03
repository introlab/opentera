from opentera.db.Base import db, BaseModel
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraServerSettings import TeraServerSettings

import uuid
import jwt
import time
import datetime


class TeraDevice(db.Model, BaseModel):
    __tablename__ = 't_devices'
    id_device = db.Column(db.Integer, db.Sequence('id_device_sequence'), primary_key=True, autoincrement=True)
    # id_site = db.Column(db.Integer, db.ForeignKey("t_sites.id_site", ondelete='cascade'), nullable=True)
    # id_session_type = db.Column(db.Integer, db.ForeignKey("t_sessions_types.id_session_type",
    #                                                       ondelete='set null'), nullable=True)
    device_uuid = db.Column(db.String(36), nullable=False, unique=True)
    device_name = db.Column(db.String, nullable=False)
    id_device_type = db.Column(db.Integer, db.ForeignKey('t_devices_types.id_device_type', ondelete='cascade'),
                               nullable=False)
    id_device_subtype = db.Column(db.Integer, db.ForeignKey('t_devices_subtypes.id_device_subtype',
                                                            ondelete='set null'), nullable=True)
    device_token = db.Column(db.String, nullable=True, unique=True)
    device_certificate = db.Column(db.String, nullable=True)
    device_enabled = db.Column(db.Boolean, nullable=False, default=False)
    device_onlineable = db.Column(db.Boolean, nullable=False, default=False)
    device_config = db.Column(db.String, nullable=True)
    device_infos = db.Column(db.String, nullable=True)
    device_notes = db.Column(db.String, nullable=True)
    device_lastonline = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    device_sites = db.relationship("TeraSite", secondary='t_devices_sites', back_populates='site_devices')
    # device_projects = db.relationship('TeraDeviceProject', cascade='delete')
    device_projects = db.relationship("TeraProject", secondary="t_devices_projects",
                                      back_populates="project_devices", lazy='joined')
    # device_session_types = db.relationship("TeraSessionTypeDeviceType")
    device_participants = db.relationship("TeraParticipant",  secondary="t_devices_participants",
                                          back_populates="participant_devices", passive_deletes=True)
    device_sessions = db.relationship("TeraSession", secondary="t_sessions_devices", back_populates="session_devices",
                                      passive_deletes=True)
    device_type = db.relationship('TeraDeviceType')
    device_subtype = db.relationship('TeraDeviceSubType')
    device_assets = db.relationship('TeraAsset', passive_deletes=True, back_populates='asset_device', lazy='select')

    authenticated = False

    # def __init__(self):
    #     self.secret = TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerDeviceTokenKey)
    #     if self.secret is None:
    #         # Fallback - should not happen
    #         self.secret = 'TeraDeviceSecret'

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields += ['device_projects', 'device_participants', 'device_sessions', 'device_certificate',
                          'device_type', 'device_subtype', 'authenticated', 'device_assets', 'device_sites']

        if minimal:
            ignore_fields += ['device_onlineable', 'device_config', 'device_notes',
                              'device_lastonline', 'device_infos',  'device_token']

        device_json = super().to_json(ignore_fields=ignore_fields)

        return device_json

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_device': self.id_device, 'device_uuid': self.device_uuid}

    def from_json(self, json):
        super().from_json(json)

        # Manage device subtype
        if type(self.device_subtype) is dict:
            self.id_device_subtype = self.device_subtype['id_device_subtype']
            self.device_subtype = None

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def is_active(self):
        return self.device_enabled

    def get_id(self):
        return self.device_uuid

    def is_login_enabled(self):
        return self.device_onlineable

    def create_token(self):
        # Creating token with user info
        payload = {
            'iss': 'TeraServer',
            'device_uuid': self.device_uuid,
            'id_device': self.id_device
        }

        self.device_token = jwt.encode(payload, TeraServerSettings.get_server_setting_value(
            TeraServerSettings.ServerDeviceTokenKey), algorithm='HS256')

        return self.device_token

    def update_last_online(self):
        self.device_lastonline = datetime.datetime.now()
        db.session.commit()

    @staticmethod
    def get_device_by_token(token):
        device = TeraDevice.query.filter_by(device_token=token).first()

        if device:
            # Validate token, key loaded from DB
            data = jwt.decode(token.encode('utf-8'),
                              TeraServerSettings.get_server_setting_value(
                                  TeraServerSettings.ServerDeviceTokenKey), algorithms='HS256')

            # Only validating UUID since other fields can change in database after token is generated.
            if data['device_uuid'] == device.device_uuid:
                device.authenticated = True
                return device
            else:
                return None

        return None

    @staticmethod
    def get_device_by_uuid(dev_uuid):
        device = TeraDevice.query.filter_by(device_uuid=dev_uuid).first()
        return device

    @staticmethod
    def get_device_by_name(name):
        return TeraDevice.query.filter_by(device_name=name).first()

    @staticmethod
    def get_device_by_id(device_id):
        return TeraDevice.query.filter_by(id_device=device_id).first()

    # @staticmethod
    # # Available device = device not assigned to any participant
    # def get_available_devices(ignore_disabled=True):
    #     if ignore_disabled:
    #         return TeraDevice.query.outerjoin(TeraDevice.device_participants)\
    #             .filter(TeraDevice.device_participants is None).all()
    #     else:
    #         return TeraDevice.query.filter_by(device_enabled=True).outerjoin(TeraDevice.device_participants).\
    #             filter(TeraDevice.device_participants is None).all()
    #
    # @staticmethod
    # # Unavailable device = device assigned to at least one participant
    # def get_unavailable_devices(ignore_disabled=True):
    #     if ignore_disabled:
    #         return TeraDevice.query.join(TeraDevice.device_participants).all()
    #     else:
    #         return TeraDevice.query.filter_by(device_enabled=True).join(TeraDevice.device_participants).all()

    @staticmethod
    def create_defaults(test=False):
        if test:
            device = TeraDevice()
            device.device_name = 'Apple Watch #W05P1'
            # Forcing uuid for tests
            device.device_uuid = 'b707e0b2-e649-47e7-a938-2b949c423f73'  # str(uuid.uuid4())
            device.id_device_type = TeraDeviceType.get_device_type_by_key('capteur').id_device_type
            # device.create_token()
            device.device_enabled = True
            device.device_onlineable = True
            # device.device_site = TeraSite.get_site_by_sitename('Default Site')
            # device.device_participants = [TeraParticipant.get_participant_by_id(1)]
            db.session.add(device)

            device2 = TeraDevice()
            device2.device_name = 'Kit Télé #1'
            device2.device_uuid = str(uuid.uuid4())
            device2.id_device_type = TeraDeviceType.get_device_type_by_key('videoconference').id_device_type
            # device2.create_token()
            device2.device_enabled = True
            device2.device_onlineable = True
            # device2.device_sites = [TeraSite.get_site_by_sitename('Default Site')]
            # device2.device_participants = [TeraParticipant.get_participant_by_id(1),
            #                               TeraParticipant.get_participant_by_id(2)]
            db.session.add(device2)

            device3 = TeraDevice()
            device3.device_name = 'Robot A'
            device3.device_uuid = str(uuid.uuid4())
            device3.id_device_type = TeraDeviceType.get_device_type_by_key('robot').id_device_type
            # device3.create_token()
            device3.device_enabled = False
            device3.device_onlineable = True
            # device3.device_sites = [TeraSite.get_site_by_sitename('Default Site')]
            # device3.device_participants = [TeraParticipant.get_participant_by_id(2)]
            db.session.add(device3)

            db.session.commit()

            # Must create token after devices are created since token contains id_device!
            device.create_token()
            device2.create_token()
            device3.create_token()

            db.session.commit()

    @classmethod
    def insert(cls, device):
        # Generate UUID
        device.device_uuid = str(uuid.uuid4())

        # Clear last online field
        device.device_lastonline = None

        # Check for device subtype
        if device.id_device_subtype == 0:
            device.id_device_subtype = None

        super().insert(device)
        # Create token
        device.create_token()
        db.session.commit()

    @classmethod
    def update(cls, update_id: int, values: dict):
        # Check for device subtype
        if 'id_device_subtype' in values:
            if values['id_device_subtype'] == 0:
                values['id_device_subtype'] = None

        # Prevent changes on UUID
        if 'device_uuid' in values:
            del values['device_uuid']

        # Remove object device_subtype
        if 'device_subtype' in values:
            del values['device_subtype']

        super().update(update_id=update_id, values=values)

    @classmethod
    def delete(cls, id_todel):
        super().delete(id_todel)

        # from opentera.db.models.TeraDeviceData import TeraDeviceData
        # TeraDeviceData.delete_files_for_device(id_todel)
