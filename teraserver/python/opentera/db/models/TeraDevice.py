from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraServerSettings import TeraServerSettings
from opentera.db.models.TeraSessionDevices import TeraSessionDevices
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant

import uuid
import jwt
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError


class TeraDevice(BaseModel, SoftDeleteMixin):
    __tablename__ = 't_devices'
    id_device = Column(Integer, Sequence('id_device_sequence'), primary_key=True, autoincrement=True)

    device_uuid = Column(String(36), nullable=False, unique=True)
    device_name = Column(String, nullable=False)
    id_device_type = Column(Integer, ForeignKey('t_devices_types.id_device_type', ondelete='cascade'), nullable=False)
    id_device_subtype = Column(Integer, ForeignKey('t_devices_subtypes.id_device_subtype',
                                                   ondelete='set null'), nullable=True)
    device_token = Column(String, nullable=True, unique=True)
    device_certificate = Column(String, nullable=True)
    device_enabled = Column(Boolean, nullable=False, default=False)
    device_onlineable = Column(Boolean, nullable=False, default=False)
    device_config = Column(String, nullable=True)
    device_infos = Column(String, nullable=True)
    device_notes = Column(String, nullable=True)
    device_lastonline = Column(TIMESTAMP(timezone=True), nullable=True)

    device_sites = relationship("TeraSite", secondary='t_devices_sites', back_populates='site_devices')
    # device_projects = relationship('TeraDeviceProject', cascade='delete')
    device_projects = relationship("TeraProject", secondary="t_devices_projects",
                                   back_populates="project_devices", lazy='selectin')
    # device_session_types = relationship("TeraSessionTypeDeviceType")
    device_participants = relationship("TeraParticipant",  secondary="t_devices_participants",
                                       back_populates="participant_devices", passive_deletes=True)
    device_sessions = relationship("TeraSession", secondary="t_sessions_devices", back_populates="session_devices",
                                   passive_deletes=True)
    device_type = relationship('TeraDeviceType')
    device_subtype = relationship('TeraDeviceSubType')
    device_created_sessions = relationship("TeraSession", cascade='delete', back_populates='session_creator_device',
                                           passive_deletes=True)

    device_service_config = relationship("TeraServiceConfig", cascade='delete', passive_deletes=True)

    device_assets = relationship("TeraAsset", cascade='delete', back_populates='asset_device', passive_deletes=True)

    device_tests = relationship("TeraTest", cascade='delete', back_populates='test_device', passive_deletes=True)

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
        TeraDevice.db().session.commit()

    @staticmethod
    def get_device_by_token(token, with_deleted: bool = False):
        device = TeraDevice.query.execution_options(include_deleted=with_deleted).filter_by(device_token=token).first()

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
    def get_device_by_certificate(certificate, with_deleted: bool = False):
        return TeraDevice.query.execution_options(include_deleted=with_deleted).\
            filter_by(device_certificate=certificate).first()

    @staticmethod
    def get_device_by_uuid(dev_uuid, with_deleted: bool = False):
        device = TeraDevice.query.execution_options(include_deleted=with_deleted).\
            filter_by(device_uuid=dev_uuid).first()
        return device

    @staticmethod
    def get_device_by_name(name, with_deleted: bool = False):
        return TeraDevice.query.execution_options(include_deleted=with_deleted).filter_by(device_name=name).first()

    @staticmethod
    def get_device_by_id(device_id, with_deleted: bool = False):
        return TeraDevice.query.execution_options(include_deleted=with_deleted).filter_by(id_device=device_id).first()

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
            TeraDevice.db().session.add(device)

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
            TeraDevice.db().session.add(device2)

            device3 = TeraDevice()
            device3.device_name = 'Robot A'
            device3.device_uuid = str(uuid.uuid4())
            device3.id_device_type = TeraDeviceType.get_device_type_by_key('robot').id_device_type
            # device3.create_token()
            device3.device_enabled = False
            device3.device_onlineable = True
            # device3.device_sites = [TeraSite.get_site_by_sitename('Default Site')]
            # device3.device_participants = [TeraParticipant.get_participant_by_id(2)]
            TeraDevice.db().session.add(device3)

            TeraDevice.db().session.commit()

            # Must create token after devices are created since token contains id_device!
            device.create_token()
            device2.create_token()
            device3.create_token()

            TeraDevice.db().session.commit()

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
        TeraDevice.db().session.commit()

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

    def delete_check_integrity(self) -> IntegrityError | None:
        # Safety check - can't delete participants with sessions
        if TeraDeviceParticipant.get_count(filters={'id_device': self.id_device}) > 0:
            return IntegrityError('Device still associated to participant(s)', self.id_device, 't_devices_participants')

        if TeraSessionDevices.get_count(filters={'id_device': self.id_device}) > 0:
            return IntegrityError('Device still has sessions', self.id_device, 't_sessions_devices')

        if TeraSession.get_count(filters={'id_creator_device': self.id_device}) > 0:
            return IntegrityError('Device still has created sessions', self.id_device, 't_sessions')

        if TeraAsset.get_count(filters={'id_device': self.id_device}) > 0:
            return IntegrityError('Device still has created assets', self.id_device, 't_assets')

        if TeraTest.get_count(filters={'id_device': self.id_device}) > 0:
            return IntegrityError('Device still has created tests', self.id_device, 't_tests')

        return None
