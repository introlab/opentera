from services.BureauActif.libbureauactif.db.Base import db, BaseModel
import uuid
import datetime
import os


class BureauActifData(db.Model, BaseModel):
    __tablename__ = "t_data"
    id_data = db.Column(db.Integer, db.Sequence('id_data_sequence'), primary_key=True, autoincrement=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        # ignore_fields.extend(['devicedata_device', 'devicedata_session', 'devicedata_uuid'])
        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        pass


