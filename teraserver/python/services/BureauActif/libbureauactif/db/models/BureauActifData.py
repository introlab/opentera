from services.BureauActif.libbureauactif.db.Base import db
from libtera.db.Base import BaseModel
import uuid
import datetime
import os
from shutil import rmtree
from services.BureauActif.FlaskModule import flask_app


class BureauActifData(db.Model, BaseModel):
    __tablename__ = "t_data"
    id_data = db.Column(db.Integer, db.Sequence('id_data_sequence'), primary_key=True, autoincrement=True)
    id_session = db.Column(db.Integer, nullable=False)
    id_device = db.Column(db.Integer, nullable=False)
    data_participant_uuid = db.Column(db.String(36), nullable=False)
    data_name = db.Column(db.String, nullable=True)
    data_original_filename = db.Column(db.String, nullable=False)
    data_saved_date = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    data_uuid = db.Column(db.String(36), nullable=False, unique=True)
    data_filesize = db.Column(db.Integer, nullable=False)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['devicedata_uuid'])
        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        pass

    @staticmethod
    def get_data_by_id(device_data_id: int):
        return BureauActifData.query.filter_by(id_device_data=device_data_id).first()

    @staticmethod
    def get_data_by_uuid(device_data_uuid):
        return BureauActifData.query.filter_by(data_uuid=device_data_uuid).first()

    @staticmethod
    def get_data_for_session(session_id: int):
        return BureauActifData.query.filter_by(id_session=session_id).all()

    @staticmethod
    def get_data_for_participant(part_uuid: str):
        return BureauActifData.query.filter_by(data_participant_uuid=part_uuid).all()

    def delete(self):
        # file_path = flask_app.config['UPLOAD_FOLDER']
        # Delete physical file from the disk
        # os.remove(os.path.join(file_path, self.devicedata_uuid))
        BureauActifData.delete_files([self])

        # Delete data from the database
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def delete_files(datas: list):
        file_path = flask_app.config['UPLOAD_FOLDER']

        for data in datas:
            file_name = os.path.join(file_path, data.data_uuid)
            if os.path.exists(file_name):
                print('BureauActifData: Deleted ' + file_name)
                os.remove(file_name)
            else:
                print('BureauActifData: File not found: ' + file_name)

    @staticmethod
    def delete_files_for_device(id_device: int):
        datas = BureauActifData.get_data_for_device(id_device)
        BureauActifData.delete_files(datas)

    @staticmethod
    def delete_files_for_session(id_session: int):
        datas = BureauActifData.get_data_for_session(id_session)
        BureauActifData.delete_files(datas)

    @staticmethod
    def delete_orphaned_files():
        # Use with caution - this will take some time to process with a lot of files...
        file_path = flask_app.config['UPLOAD_FOLDER']
        for file in os.listdir(file_path):
            if not BureauActifData.get_data_by_uuid(file):
                file_name = os.path.join(file_path, file)
                print('BureauActifData: Orphaned file found and deleted: ' + file_name)
                os.remove(file_name)

