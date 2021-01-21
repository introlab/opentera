from opentera.db.Base import db, BaseModel
import uuid
from enum import Enum, unique
from sqlalchemy import or_


@unique
class AssetType(Enum):
    RAW_FILE = 1
    RAW_DATA = 2
    RESULT_FILE = 3
    PROCESSED_DATA = 4
    REPORT = 5

    def describe(self):
        return self.name, self.value


class TeraAsset(db.Model, BaseModel):
    __tablename__ = 't_assets'
    id_asset = db.Column(db.Integer, db.Sequence('id_asset_sequence'), primary_key=True, autoincrement=True)
    id_session = db.Column(db.Integer, db.ForeignKey("t_sessions.id_session", ondelete='cascade'), nullable=False)
    id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device"), nullable=True)
    id_participant = db.Column(db.Integer, db.ForeignKey("t_participants.id_participant"),
                               nullable=True)
    id_user = db.Column(db.Integer, db.ForeignKey("t_users.id_user"), nullable=True)
    # Put a description of the asset here
    asset_name = db.Column(db.String, nullable=False)

    asset_uuid = db.Column(db.String(36), nullable=False, unique=True)
    asset_service_uuid = db.Column(db.String(36), nullable=False)
    asset_type = db.Column(db.Integer, nullable=False)

    asset_session = db.relationship("TeraSession")
    asset_device = db.relationship("TeraDevice")
    asset_user = db.relationship("TeraUser")
    asset_participant = db.relationship("TeraParticipant")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['asset_session', 'asset_device', 'asset_user', 'asset_participant'])

        return super().to_json(ignore_fields=ignore_fields)

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
                new_asset.asset_type = AssetType.RAW_FILE.value
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
            new_asset.asset_type = AssetType.PROCESSED_DATA.value
            db.session.add(new_asset)

            db.session.commit()

    @staticmethod
    def get_asset_by_id(asset_id: int):
        return TeraAsset.query.filter_by(id_asset=asset_id).first()

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
    def get_assets_for_service(service_uuid: str):
        return TeraAsset.query.filter_by(service_uuid=service_uuid).all()

    @classmethod
    def insert(cls, asset):
        # Generate UUID
        asset.asset_uuid = str(uuid.uuid4())

        super().insert(asset)
