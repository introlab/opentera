from services.BureauActif.libbureauactif.db.Base import db, BaseModel


class BureauActifParticipantInfo(db.Model, BaseModel):
    __tablename__ = "ba_participants_infos"
    id_participant_info = db.Column(db.Integer, db.Sequence('id_participant_info_sequence'), primary_key=True,
                                    autoincrement=True)
    participant_info_participant_uuid = db.Column(db.String(36), nullable=False, unique=True)
    participant_info_last_ip = db.Column(db.String, nullable=True)
    participant_info_script_version = db.Column(db.String, nullable=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['id_participant_info'])
        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        pass

    @staticmethod
    def get_infos_for_participant(part_uuid: str):
        return BureauActifParticipantInfo.query.filter_by(participant_info_participant_uuid=part_uuid).first()

