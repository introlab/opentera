# from flask_restx import Resource
# from flask_babel import gettext
# from modules.FlaskModule.Views.Upload import ALLOWED_EXTENSIONS
# from modules.LoginModule.LoginModule import LoginModule, current_device
# from flask import request
# from werkzeug.utils import secure_filename
# from modules.FlaskModule.FlaskModule import flask_app
#
# from opentera.db.models.TeraDeviceData import TeraDeviceData
# from opentera.db.models.TeraSessionEvent import TeraSessionEvent
# from modules.DatabaseModule.DBManager import DBManager
# from opentera.db.Base import db
#
# import datetime
# import uuid
# import os
#
#
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
#
# class DeviceUpload(Resource):
#
#     def __init__(self, _api, flaskModule=None):
#         Resource.__init__(self, _api)
#         self.module = flaskModule
#
#     @LoginModule.device_token_or_certificate_required
#     def get(self):
#         print(request)
#         print('current_device', current_device)
#         return '', 200
#
#     @LoginModule.device_token_or_certificate_required
#     def post(self):
#         # print(request)
#         # print('current_device', current_device)
#
#         if request.content_type == 'application/octet-stream':
#             if 'X-Id-Session' not in request.headers:
#                 return gettext('No ID Session specified'), 400
#
#             if 'X-Filename' not in request.headers:
#                 return gettext('No file specified'), 400
#
#             id_session = int(request.headers['X-Id-Session'])
#             filename = secure_filename(request.headers['X-Filename'])
#             creation_date = datetime.datetime.strptime(request.headers['X-Filedate'], '%Y-%m-%d %H:%M:%S')
#
#             # Check if device is allowed to access the specified session
#             device_access = DBManager.deviceAccess(current_device)
#             file_session = device_access.query_session(session_id=id_session)
#             if not file_session:
#                 return '', 403
#
#             # Create file entry in database
#             file_db_entry = TeraDeviceData()
#             file_db_entry.devicedata_device = current_device
#             # file_db_entry.devicedata_session = file_session
#             file_db_entry.id_session = id_session
#             file_db_entry.devicedata_original_filename = filename
#             file_db_entry.devicedata_name = filename
#             file_db_entry.devicedata_saved_date = creation_date
#             file_db_entry.devicedata_uuid = str(uuid.uuid4())
#             file_db_entry.devicedata_filesize = len(request.data)
#             db.session.add(file_db_entry)
#             db.session.commit()
#
#             # Save file on disk
#             fo = open(os.path.join(flask_app.config['UPLOAD_FOLDER'], file_db_entry.devicedata_uuid), "wb")
#             fo.write(request.data)
#             fo.close()
#
#             # Parse events if requested
#             if request.headers.__contains__('X-Parse-Logfile-Events'):
#                 print('Parsing events')
#                 with open(os.path.join(flask_app.config['UPLOAD_FOLDER'], file_db_entry.devicedata_uuid), "r") as fp:
#                     for line in fp:
#                         parts = line.strip('\n').split('\t')
#                         if len(parts) == 5:
#                             # Valid log
#                             timestamp = datetime.datetime.fromtimestamp(float(parts[0]))
#                             event_type = int(parts[1])
#                             context = parts[2]
#                             # Skipping formatted datetime at parts[3]
#                             log_data = parts[4]
#
#                             event = TeraSessionEvent()
#                             event.id_session = id_session
#                             event.session_event_datetime = timestamp
#                             event.id_session_event_type = event_type
#                             event.session_event_context = context
#                             event.session_event_text = log_data
#
#                             db.session.add(event)
#                             db.session.commit()
#
#             return '', 200
#
#         elif request.content_type.__contains__('multipart/form-data'):
#             if 'id_session' not in request.form:
#                 return gettext('No ID Session specified'), 400
#
#             # check if the post request has the file part
#             if 'file' not in request.files:
#                 return gettext('No file specified'), 400
#
#             file = request.files['file']
#             id_session = int(request.form['id_session'])
#
#             # Check if device is allowed to access the specified session
#             device_access = DBManager.deviceAccess(current_device)
#             file_session = device_access.query_session(session_id=id_session)
#             if not file_session:
#                 return '', 403
#
#             # if user does not select file, browser also
#             # submit an empty part without filename
#             if file.filename == '':
#                 return gettext('No filename specified'), 400
#
#             if file:
#                 filename = secure_filename(file.filename)
#
#                 # Create file entry in database
#                 file_db_entry = TeraDeviceData()
#                 file_db_entry.devicedata_device = current_device
#                 # file_db_entry.devicedata_session = file_session
#                 file_db_entry.id_session = id_session
#                 file_db_entry.devicedata_original_filename = filename
#                 file_db_entry.devicedata_saved_date = datetime.datetime.now()
#                 file_db_entry.devicedata_uuid = str(uuid.uuid4())
#                 db.session.add(file_db_entry)
#                 db.session.commit()
#
#                 # Save file on disk
#                 file.save(os.path.join(flask_app.config['UPLOAD_FOLDER'], file_db_entry.devicedata_uuid))
#                 return '', 200
#
#         return '', 400
