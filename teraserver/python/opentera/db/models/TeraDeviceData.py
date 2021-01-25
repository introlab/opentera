# from opentera.db.Base import db, BaseModel
# import uuid
# import datetime
# import os
# from shutil import rmtree
# from modules.FlaskModule.FlaskModule import flask_app
#
#
# class TeraDeviceData(db.Model, BaseModel):
#     __tablename__ = "t_devices_data"
#     id_device_data = db.Column(db.Integer, db.Sequence("id_device_data_sequence"), primary_key=True, autoincrement=True)
#     id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device", ondelete='cascade'), nullable=False)
#     id_session = db.Column(db.Integer, db.ForeignKey("t_sessions.id_session", ondelete='cascade'), nullable=False)
#     devicedata_name = db.Column(db.String, nullable=True)
#     devicedata_original_filename = db.Column(db.String, nullable=False)
#     devicedata_saved_date = db.Column(db.TIMESTAMP, nullable=False)
#     devicedata_uuid = db.Column(db.String(36), nullable=False, unique=True)
#     devicedata_filesize = db.Column(db.Integer, nullable=False)
#
#     devicedata_device = db.relationship("TeraDevice")
#     devicedata_session = db.relationship("TeraSession")
#
#     def to_json(self, ignore_fields=None, minimal=False):
#         if ignore_fields is None:
#             ignore_fields = []
#
#         ignore_fields.extend(['devicedata_device', 'devicedata_session', 'devicedata_uuid'])
#         rval = super().to_json(ignore_fields=ignore_fields)
#
#         return rval
#
#     @staticmethod
#     def get_data_for_device(device_id: int):
#         return TeraDeviceData.query.filter_by(id_device=device_id).all()
#
#     @staticmethod
#     def get_data_by_id(device_data_id: int):
#         return TeraDeviceData.query.filter_by(id_device_data=device_data_id).first()
#
#     @staticmethod
#     def get_data_by_uuid(device_data_uuid):
#         return TeraDeviceData.query.filter_by(devicedata_uuid=device_data_uuid).first()
#
#     @staticmethod
#     def get_data_for_session(session_id: int):
#         return TeraDeviceData.query.filter_by(id_session=session_id).all()
#
#     @staticmethod
#     def get_data_for_participant(part_id: int):
#         from opentera.db.models.TeraSession import TeraSession
#         from opentera.db.models.TeraParticipant import TeraParticipant
#         return TeraDeviceData.query.join(TeraSession).filter(TeraSession.session_participants.
#                                                              any(id_participant=part_id)).all()
#
#     @staticmethod
#     def create_defaults(upload_path: str):
#         from .TeraSession import TeraSession
#         from .TeraDevice import TeraDevice
#         import os
#
#         # Clear all files in upload path
#         if os.path.exists(upload_path):
#             rmtree(upload_path)
#
#         if not os.path.exists(upload_path):
#              os.mkdir(upload_path)
#
#         base_session = TeraSession.get_session_by_name('Séance #1')
#         base_device = TeraDevice.get_device_by_name('Apple Watch #W05P1')
#         data1 = TeraDeviceData()
#         data1.id_device = base_device.id_device
#         data1.id_session = base_session.id_session
#         data1.devicedata_name = 'Test Data #1'
#         data1.devicedata_original_filename = 'Data1.data'
#         data1.devicedata_saved_date = datetime.datetime.now()
#         data1.devicedata_uuid = str(uuid.uuid4())
#         # Create "file"
#         filesize = 1024 * 1024
#         with open(upload_path + '/' + data1.devicedata_uuid, 'wb') as fout:
#             fout.write(os.urandom(filesize))
#         data1.devicedata_filesize = filesize
#         db.session.add(data1)
#
#         data2 = TeraDeviceData()
#         data2.id_device = base_device.id_device
#         data2.id_session = base_session.id_session
#         data2.devicedata_name = 'Test Data #2'
#         data2.devicedata_original_filename = 'Data2.data'
#         data2.devicedata_saved_date = datetime.datetime.now()
#         data2.devicedata_uuid = str(uuid.uuid4())
#         # Create "file"
#         filesize = 1024 * 1024 * 10
#         with open(upload_path + '/' + data2.devicedata_uuid, 'wb') as fout:
#             fout.write(os.urandom(filesize))
#         data2.devicedata_filesize = filesize
#         db.session.add(data2)
#         db.session.commit()
#
#     def delete(self):
#         # file_path = flask_app.config['UPLOAD_FOLDER']
#         # Delete physical file from the disk
#         # os.remove(os.path.join(file_path, self.devicedata_uuid))
#         TeraDeviceData.delete_files([self])
#
#         # Delete data from the database
#         db.session.delete(self)
#         db.session.commit()
#
#     @staticmethod
#     def delete_files(datas: list):
#         file_path = flask_app.config['UPLOAD_FOLDER']
#
#         for data in datas:
#             file_name = os.path.join(file_path, data.devicedata_uuid)
#             if os.path.exists(file_name):
#                 print('TeraDeviceData: Deleted ' + file_name)
#                 os.remove(file_name)
#             else:
#                 print('TeraDeviceData: File not found: ' + file_name)
#
#     @staticmethod
#     def delete_files_for_device(id_device: int):
#         datas = TeraDeviceData.get_data_for_device(id_device)
#         TeraDeviceData.delete_files(datas)
#
#     @staticmethod
#     def delete_files_for_session(id_session: int):
#         datas = TeraDeviceData.get_data_for_session(id_session)
#         TeraDeviceData.delete_files(datas)
#
#     @staticmethod
#     def delete_orphaned_files():
#         # Use with caution - this will take some time to process with a lot of files...
#         file_path = flask_app.config['UPLOAD_FOLDER']
#         for file in os.listdir(file_path):
#             if not TeraDeviceData.get_data_by_uuid(file):
#                 file_name = os.path.join(file_path, file)
#                 print('TeraDeviceData: Orphaned file found and deleted: ' + file_name)
#                 os.remove(file_name)
#
