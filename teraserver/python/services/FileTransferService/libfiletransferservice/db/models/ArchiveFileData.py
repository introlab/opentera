
from opentera.db.Base import BaseModel
from sqlalchemy import exc
from sqlalchemy import Column, ForeignKey, Sequence, Integer, String, BigInteger, TIMESTAMP
import os
from enum import Enum
from datetime import datetime


class TeraArchiveStatus(Enum):
    STATUS_PENDING = 0
    STATUS_INPROGRESS = 1
    STATUS_COMPLETED = 2
    STATUS_CANCELLED = 3
    STATUS_TERMINATED = 4


class ArchiveFileData(BaseModel):
    __tablename__ = "t_archive_file_data"
    id_archive_file_data = Column(Integer, Sequence('id_archive_file_data_sequence'), primary_key=True,
                                  autoincrement=True)
    archive_uuid = Column(String(36), nullable=False, unique=True)
    archive_original_filename = Column(String, nullable=False)
    archive_file_size = Column(BigInteger, nullable=False, default=0)

    archive_datetime = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: str(datetime.now()))
    archive_expiration_datetime = Column(TIMESTAMP(timezone=True), nullable=True)
    archive_status = Column(Integer, nullable=False, default=TeraArchiveStatus.STATUS_PENDING.value)
    archive_owner_uuid = Column(String(36), nullable=False)

    @staticmethod
    def get_archive_by_uuid(uuid_archive: str):
        return ArchiveFileData.query.filter_by(archive_uuid=uuid_archive).first()

    @staticmethod
    def get_archive_by_id(id_archive: int):
        return ArchiveFileData.query.filter_by(id_archive_file_data=id_archive).first()

    # Delete this archive. file_folder is required to delete the file too.
    def delete_file_archive(self, file_folder: str) -> bool:
        # Delete related file from system
        file_name = os.path.join(file_folder, self.archive_uuid)
        if os.path.exists(file_name):
            os.remove(file_name)
        else:
            return False

        # Delete self from database
        try:
            self.db().session.delete(self)
            self.commit()
        except exc.SQLAlchemyError:
            return False

        return True

