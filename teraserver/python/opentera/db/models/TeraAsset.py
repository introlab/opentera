from opentera.db.Base import db, BaseModel
import uuid
# from enum import Enum, unique
from sqlalchemy import or_


# @unique
# class AssetType(Enum):
#     RAW_FILE = 1
#     RAW_DATA = 2
#     RESULT_FILE = 3
#     PROCESSED_DATA = 4
#     REPORT = 5
#
#     def describe(self):
#         return self.name, self.value


class TeraAsset(db.Model, BaseModel):
    __tablename__ = 't_assets'
    id_asset = db.Column(db.Integer, db.Sequence('id_asset_sequence'), primary_key=True, autoincrement=True)
    id_session = db.Column(db.Integer, db.ForeignKey("t_sessions.id_session", ondelete='cascade'), nullable=False)
    # Creator of that asset - multiple could be used to indicate, for example, an asset created by a device for a
    # specific participant in a session
    id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device"), nullable=True)
    id_participant = db.Column(db.Integer, db.ForeignKey("t_participants.id_participant"), nullable=True)
    id_user = db.Column(db.Integer, db.ForeignKey("t_users.id_user"), nullable=True)
    id_service = db.Column(db.Integer, db.ForeignKey("t_services.id_service"), nullable=True)
    # Put a description of the asset here
    asset_name = db.Column(db.String, nullable=False)

    asset_uuid = db.Column(db.String(36), nullable=False, unique=True)
    asset_service_uuid = db.Column(db.String(36), db.ForeignKey("t_services.service_uuid", ondelete='cascade'),
                                   nullable=False)
    asset_type = db.Column(db.String, nullable=False)  # MIME Type
    asset_datetime = db.Column(db.TIMESTAMP(timezone=True), nullable=True)

    asset_session = db.relationship("TeraSession", back_populates='session_assets')
    asset_device = db.relationship("TeraDevice", back_populates='device_assets')
    asset_user = db.relationship("TeraUser")
    asset_participant = db.relationship("TeraParticipant")
    asset_service = db.relationship("TeraService", foreign_keys="TeraAsset.id_service")
    asset_service_owner = db.relationship("TeraService", foreign_keys="TeraAsset.asset_service_uuid")

    def from_json(self, json, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['asset_session', 'asset_device', 'asset_user', 'asset_participant', 'asset_service',
                              'asset_service_owner', 'asset_service_owner_name', 'asset_session_name'])

        super().from_json(json, ignore_fields)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['asset_session', 'asset_device', 'asset_user', 'asset_participant', 'asset_service',
                              'asset_service_owner', 'asset_service_owner_name', 'asset_session_name'])

        asset_json = super().to_json(ignore_fields=ignore_fields)
        if not minimal:
            asset_json['asset_service_owner_name'] = self.asset_service_owner.service_name
            asset_json['asset_session_name'] = self.asset_session.session_name
            if self.id_device:
                asset_json['asset_device'] = self.asset_device.device_name
            if self.id_user:
                asset_json['asset_user'] = self.asset_user.get_fullname()
            if self.id_participant:
                asset_json['asset_participant'] = self.asset_participant.participant_name
            if self.id_service:
                asset_json['asset_service'] = self.asset_service.service_name

        return asset_json

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_asset': self.id_asset, 'asset_uuid': self.asset_uuid}

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraSession import TeraSession
            from opentera.db.models.TeraDevice import TeraDevice
            from opentera.db.models.TeraParticipant import TeraParticipant
            from opentera.db.models.TeraUser import TeraUser

            session2 = TeraSession.get_session_by_name("Séance #2")
            session3 = TeraSession.get_session_by_name("Séance #3")

            for i in range(3):
                new_asset = TeraAsset()
                new_asset.asset_name = "Asset #" + str(i)
                new_asset.asset_session = session2
                new_asset.asset_uuid = str(uuid.uuid4())
                new_asset.asset_service_uuid = '00000000-0000-0000-0000-000000000001'
                new_asset.asset_type = 'application/octet-stream'
                if i == 0:
                    new_asset.id_participant = TeraParticipant.get_participant_by_name('Participant #1').id_participant
                if i == 1:
                    new_asset.id_user = TeraUser.get_user_by_id(1).id_user
                db.session.add(new_asset)

            asset_device = TeraDevice.get_device_by_name('Apple Watch #W05P1')
            new_asset = TeraAsset()
            new_asset.asset_name = "Device Asset"
            new_asset.asset_session = session3
            new_asset.asset_device = asset_device
            new_asset.asset_uuid = str(uuid.uuid4())
            new_asset.asset_service_uuid = '00000000-0000-0000-0000-000000000001'
            new_asset.asset_type = 'video/mpeg'
            new_asset.id_service = 1
            db.session.add(new_asset)

            db.session.commit()

    @staticmethod
    def get_asset_by_id(asset_id: int):
        return TeraAsset.query.filter_by(id_asset=asset_id).first()

    @staticmethod
    def get_asset_by_uuid(asset_uuid: str):
        return TeraAsset.query.filter_by(asset_uuid=asset_uuid).first()

    @staticmethod
    def get_assets_for_device(device_id: int):
        # return TeraAsset.query.filter_by(id_device=device_id).all()
        from opentera.db.models.TeraSession import TeraSession
        return TeraAsset.query.join(TeraSession).filter(or_(TeraSession.session_devices.any(
            id_device=device_id), TeraAsset.id_device == device_id)).all()

    @staticmethod
    def get_assets_for_user(user_id: int):
        from opentera.db.models.TeraSession import TeraSession
        return TeraAsset.query.join(TeraSession).filter(or_(TeraSession.session_users.any(
            id_user=user_id), TeraAsset.id_user == user_id)).all()

    @staticmethod
    def get_assets_for_session(session_id: int):
        return TeraAsset.query.filter_by(id_session=session_id).all()

    @staticmethod
    def get_assets_for_participant(part_id: int):
        from opentera.db.models.TeraSession import TeraSession
        return TeraAsset.query.join(TeraSession).filter(or_(TeraSession.session_participants.any(
            id_participant=part_id), TeraAsset.id_participant == part_id)).all()

    @staticmethod
    def get_assets_owned_by_service(service_uuid: str):
        return TeraAsset.query.filter_by(asset_service_uuid=service_uuid).all()

    @staticmethod
    def get_assets_created_by_service(service_id: int):
        return TeraAsset.query.filter_by(id_service=service_id).all()

    @staticmethod
    def get_assets_created_by_user(user_id: int):
        return TeraAsset.query.filter_by(id_user=user_id).all()

    @staticmethod
    def get_assets_created_by_participant(participant_id: int):
        return TeraAsset.query.filter_by(id_participant=participant_id).all()

    @staticmethod
    def get_assets_created_by_device(device_id: int):
        return TeraAsset.query.filter_by(id_device=device_id).all()

    @staticmethod
    def get_access_token(asset_uuids: list, token_key: str, requester_uuid: str, expiration=3600):
        import time
        import jwt

        # Creating token with user info
        now = time.time()
        payload = {
            'iat': int(now),
            'exp': int(now) + expiration,
            'iss': 'TeraServer',
            'asset_uuids': asset_uuids,
            'requester_uuid': requester_uuid
        }

        return jwt.encode(payload, token_key, algorithm='HS256')

    @classmethod
    def insert(cls, asset):
        # Generate UUID
        asset.asset_uuid = str(uuid.uuid4())

        super().insert(asset)
