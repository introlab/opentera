from libtera.db.Base import db, BaseModel
import uuid
import datetime
import os
from shutil import rmtree


class TeraDeviceData(db.Model, BaseModel):
    __tablename__ = "t_devices_data"
    id_device_data = db.Column(db.Integer, db.Sequence("id_device_data_sequence"), primary_key=True, autoincrement=True)
    id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device", ondelete='cascade'), nullable=False)
    id_session = db.Column(db.Integer, db.ForeignKey("t_sessions.id_session", ondelete='cascade'), nullable=False)
    devicedata_name = db.Column(db.String, nullable=True)
    devicedata_original_filename = db.Column(db.String, nullable=False)
    devicedata_saved_date = db.Column(db.TIMESTAMP, nullable=False)
    devicedata_uuid = db.Column(db.String(36), nullable=False, unique=True)

    devicedata_device = db.relationship("TeraDevice")
    devicedata_session = db.relationship("TeraSession")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['devicedata_device', 'devicedata_session', 'devicedata_uuid'])
        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def get_data_for_device(device_id: int):
        return TeraDeviceData.query.filter_by(id_device=device_id).all()

    @staticmethod
    def get_data_by_id(device_data_id: int):
        return TeraDeviceData.query.filter_by(id_device_data=device_data_id).first()

    @staticmethod
    def get_data_for_session(session_id: int):
        return TeraDeviceData.query.filter_by(id_session=session_id).all()

    @staticmethod
    def create_defaults(upload_path: str):
        from .TeraSession import TeraSession
        from .TeraDevice import TeraDevice
        import os

        # Clear all files in upload path
        rmtree(upload_path)
        os.mkdir(upload_path)

        base_session = TeraSession.get_session_by_name('Séance #1')
        base_device = TeraDevice.get_device_by_name('Apple Watch #W05P1')
        data1 = TeraDeviceData()
        data1.id_device = base_device.id_device
        data1.id_session = base_session.id_session
        data1.devicedata_name = 'Test Data #1'
        data1.devicedata_original_filename = 'Data1.data'
        data1.devicedata_saved_date = datetime.datetime.now()
        data1.devicedata_uuid = str(uuid.uuid4())
        # Create "file"
        with open(upload_path + '/' + data1.devicedata_uuid, 'wb') as fout:
            fout.write(os.urandom(1024 * 1024))
        db.session.add(data1)

        data2 = TeraDeviceData()
        data2.id_device = base_device.id_device
        data2.id_session = base_session.id_session
        data2.devicedata_name = 'Test Data #2'
        data2.devicedata_original_filename = 'Data2.data'
        data2.devicedata_saved_date = datetime.datetime.now()
        data2.devicedata_uuid = str(uuid.uuid4())
        # Create "file"
        with open(upload_path + '/' + data2.devicedata_uuid, 'wb') as fout:
            fout.write(os.urandom(1024 * 1024 * 10))
        db.session.add(data2)
        db.session.commit()

    def delete(self, file_path):
        # Delete physical file from the disk
        os.remove(os.path.join(file_path, self.devicedata_uuid))

        # Delete data from the database
        db.session.delete(self)
        db.session.commit()

