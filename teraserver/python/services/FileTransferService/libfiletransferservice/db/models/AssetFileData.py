from services.FileTransferService.libfiletransferservice.db.Base import db
from opentera.db.Base import BaseModel
import os


class AssetFileData(db.Model, BaseModel):
    __tablename__ = "t_asset_file_data"
    id_asset_file_data = db.Column(db.Integer, db.Sequence('id_asset_file_data_sequence'),
                                   primary_key=True, autoincrement=True)

    asset_uuid = db.Column(db.String(36), nullable=False, unique=True)
    asset_creator_service_uuid = db.Column(db.String(36), nullable=False, unique=False)
    asset_original_filename = db.Column(db.String, nullable=False)
    asset_saved_date = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    asset_file_size = db.Column(db.Integer, nullable=False)
    asset_md5 = db.Column(db.String, nullable=False)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        return super().to_json(ignore_fields=ignore_fields)

    def delete(self):
        AssetFileData.delete_files([self])

        # Delete data from the database
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def delete_files(assets: list):
        # Get upload path from configuration
        from services.FileTransferService.Globals import config_man
        file_path = config_man.filetransfer_config['upload_directory']

        for data in assets:
            file_name = os.path.join(file_path, data.devicedata_uuid)
            if os.path.exists(file_name):
                print('AssetFileData: Deleted ' + file_name)
                os.remove(file_name)
            else:
                print('AssetFileData: File not found: ' + file_name)
