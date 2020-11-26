from services.BureauActif.libbureauactif.db.Base import db, BaseModel


class BureauActifDeviceInfo(db.Model, BaseModel):
    __tablename__ = "ba_devices_infos"
    id_device_info = db.Column(db.Integer, db.Sequence('id_device_info_sequence'), primary_key=True, autoincrement=True)
    device_info_device_uuid = db.Column(db.String(36), nullable=False, unique=True)
    device_info_last_ip = db.Column(db.String, nullable=True)
    device_info_script_version = db.Column(db.String, nullable=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['id_device_info'])
        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        pass

    @staticmethod
    def get_infos_for_device(device_uuid: str):
        return BureauActifDeviceInfo.query.filter_by(device_info_device_uuid=device_uuid).first()

